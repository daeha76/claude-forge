---
name: zdog-animations
description: Zdog 애니메이션 패턴 - 회전/이동 루프, easing, spring, 순차 등장
metadata:
  tags: [zdog, animation, easing, spring, requestAnimationFrame]
---

# Zdog Animations

## 기본 애니메이션 루프

```js
function animate() {
  // 1. 상태 업데이트
  illo.rotate.y += 0.03;

  // 2. 렌더 그래프 갱신 (MUST)
  illo.updateRenderGraph();

  // 3. 다음 프레임 요청
  requestAnimationFrame(animate);
}
animate();
```

### MUST

- `updateRenderGraph()`는 매 프레임 반드시 호출
- `animate()` 내부에서 new Shape() 생성 금지 (메모리 누수)
- 상태 변경 → updateRenderGraph → requestAnimationFrame 순서 유지

## 회전 애니메이션

### 단축 자동 회전

```js
function animate() {
  illo.rotate.y += 0.03;   // Y축 회전
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

### 특정 도형만 회전

```js
const head = new Zdog.Ellipse({ addTo: illo, diameter: 60, stroke: 20, color: '#636' });

function animate() {
  head.rotate.z += 0.02;   // head만 회전
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

### 시간 기반 회전 (일정 속도 보장)

```js
let lastTime = performance.now();

function animate(currentTime) {
  const delta = (currentTime - lastTime) / 1000; // 초 단위
  lastTime = currentTime;

  illo.rotate.y += delta * Math.PI; // 초당 180도
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
```

## 이동 애니메이션

### translate 이동

```js
let t = 0;

function animate() {
  t += 0.02;
  shape.translate.x = Math.sin(t) * 40;  // 좌우 왕복
  shape.translate.y = Math.cos(t) * 20;  // 상하 왕복
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

## Easing 함수

### easeInOut (sine)

```js
function easeInOut(t) {
  return 0.5 - Math.cos(t * Math.PI) / 2;
}
```

### easeOutBack (탄성 오버슈트)

```js
function easeOutBack(t) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
}
```

### easeOutElastic

```js
function easeOutElastic(t) {
  if (t === 0 || t === 1) return t;
  return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (2 * Math.PI / 3)) + 1;
}
```

### 적용 패턴

```js
const DURATION = 60; // 프레임 수
let frame = 0;

function animate() {
  if (frame < DURATION) {
    const progress = easeInOut(frame / DURATION);
    shape.translate.y = -100 + progress * 100; // -100 → 0
    shape.rotate.z = progress * Zdog.TAU;      // 0 → 360도
    frame++;
  }

  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

## Lerp (선형 보간)

```js
function lerp(start, end, t) {
  return start + (end - start) * t;
}

// 사용: 부드러운 추적
function animate() {
  shape.translate.x = lerp(shape.translate.x, targetX, 0.1);
  shape.translate.y = lerp(shape.translate.y, targetY, 0.1);
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

## Spring 애니메이션

```js
function createSpring({ stiffness = 0.1, damping = 0.8 } = {}) {
  let velocity = 0;
  let current = 0;

  return {
    update(target) {
      const force = (target - current) * stiffness;
      velocity = (velocity + force) * damping;
      current += velocity;
      return current;
    },
    get value() { return current; },
    set value(v) { current = v; velocity = 0; },
  };
}

// 사용
const springY = createSpring({ stiffness: 0.08, damping: 0.85 });

function animate() {
  shape.translate.y = springY.update(targetY);
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

## 순차 등장 (Staggered)

```js
const shapes = [];
const STAGGER_DELAY = 10; // 각 도형 간 프레임 지연
const ANIM_DURATION = 30;

// 도형 생성
for (let i = 0; i < 5; i++) {
  shapes.push({
    shape: new Zdog.Rect({
      addTo: illo,
      width: 40, height: 40,
      stroke: 5,
      color: `hsl(${i * 72}, 70%, 50%)`,
      fill: true,
      translate: { x: -80 + i * 40 },
      scale: 0, // 초기: 안 보임
    }),
    delay: i * STAGGER_DELAY,
  });
}

let frame = 0;

function animate() {
  shapes.forEach(({ shape, delay }) => {
    const localFrame = frame - delay;
    if (localFrame >= 0 && localFrame <= ANIM_DURATION) {
      const t = easeOutBack(localFrame / ANIM_DURATION);
      shape.scale = t;
    }
  });

  frame++;
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();
```

## isSpinning 패턴 (관성 드래그 + 자동 회전)

```js
let isSpinning = true;

// 드래그 시작 → 자동 회전 중지
illo.onDragStart = function () {
  isSpinning = false;
};

// 드래그 종료 → 자동 회전 재개 (선택)
illo.onDragEnd = function () {
  isSpinning = true;
};

function animate() {
  if (isSpinning) {
    illo.rotate.y += 0.03;
  }
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();
```

## Zdog.TAU 상수

```js
Zdog.TAU // = Math.PI * 2 (360도)

// 90도 회전
shape.rotate.x = Zdog.TAU / 4;

// 45도 회전
shape.rotate.z = Zdog.TAU / 8;
```

## FORBIDDEN

- `animate()` 내에서 `new Zdog.*()` 호출 (프레임마다 도형 생성 = 메모리 누수)
- `setInterval` 사용 (requestAnimationFrame이 프레임 동기화에 적합)
- `updateRenderGraph()` 누락 (화면이 갱신되지 않음)
