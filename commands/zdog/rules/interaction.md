---
name: zdog-interaction
description: Zdog 인터랙션 - Dragger, dragRotate, 터치/펜 지원, isSpinning
metadata:
  tags: [zdog, interaction, drag, touch, dragger]
---

# Zdog Interaction

## dragRotate (가장 간단)

Illustration에 `dragRotate: true`를 설정하면 마우스/터치 드래그로 씬 전체를 회전할 수 있다.

```js
const illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  zoom: 4,
  dragRotate: true,   // 이것만으로 드래그 회전 활성화
});
```

### 드래그 콜백

```js
const illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  dragRotate: true,
  onDragStart: function () {
    console.log('drag started');
  },
  onDragMove: function (pointer, moveX, moveY) {
    console.log('dragging', moveX, moveY);
  },
  onDragEnd: function () {
    console.log('drag ended');
  },
});
```

## Dragger 클래스 (커스텀 인터랙션)

dragRotate보다 세밀한 제어가 필요할 때 Dragger를 직접 사용한다.

```js
const dragger = new Zdog.Dragger({
  startElement: document.querySelector('.zdog-canvas'),
  onDragStart: function (pointer, moveX, moveY) {
    // 드래그 시작
  },
  onDragMove: function (pointer, moveX, moveY) {
    // moveX, moveY: 이전 프레임 대비 이동량 (px)
    shape.translate.x += moveX;
    shape.translate.y += moveY;
  },
  onDragEnd: function () {
    // 드래그 종료
  },
});
```

### Dragger 프로퍼티

| 프로퍼티 | 타입 | 설명 |
|----------|------|------|
| startElement | Element | 드래그 시작 감지 요소 |
| onDragStart | Function(pointer, moveX, moveY) | 드래그 시작 콜백 |
| onDragMove | Function(pointer, moveX, moveY) | 드래그 중 콜백 |
| onDragEnd | Function() | 드래그 종료 콜백 |

### pointer 객체

- `pointer.pageX`, `pointer.pageY`: 페이지 기준 좌표
- 마우스, 터치, 펜 입력 모두 통합 처리됨

## 축 제한 드래그 회전

```js
let dragStartRX, dragStartRY;

const illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  zoom: 4,
  onDragStart: function () {
    dragStartRX = illo.rotate.x;
    dragStartRY = illo.rotate.y;
  },
  onDragMove: function (pointer, moveX, moveY) {
    // Y축 회전만 허용 (가로 드래그)
    illo.rotate.y = dragStartRY + moveX / 200;
    // X축 회전 제한 (-45도 ~ 45도)
    const rx = dragStartRX - moveY / 200;
    illo.rotate.x = Math.max(-Zdog.TAU / 8, Math.min(Zdog.TAU / 8, rx));
  },
});
```

## isSpinning 패턴 (자동 회전 + 드래그)

```js
let isSpinning = true;

const illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  zoom: 4,
  dragRotate: true,
  onDragStart: function () {
    isSpinning = false;
  },
});

function animate() {
  if (isSpinning) {
    illo.rotate.y += 0.03;
  }
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();

// 선택: 드래그 종료 후 일정 시간 뒤 자동 회전 재개
illo.onDragEnd = function () {
  setTimeout(() => { isSpinning = true; }, 2000);
};
```

## 터치 & 펜 지원

Zdog의 Dragger는 자동으로 마우스/터치/펜 이벤트를 통합 처리한다.

```
mousedown  → onDragStart
mousemove  → onDragMove
mouseup    → onDragEnd

touchstart → onDragStart
touchmove  → onDragMove
touchend   → onDragEnd

pointerdown → onDragStart (Pointer Events도 지원)
```

### 주의사항

- `touch-action: none` CSS 설정 필요 (스크롤 방지)
- Canvas에 적용: `canvas { touch-action: none; }`

## 커스텀 인터랙션 예제: 도형 개별 드래그

```js
// 특정 도형을 드래그로 이동
const draggableShape = new Zdog.Rect({
  addTo: illo,
  width: 60, height: 60,
  stroke: 10,
  color: '#E62',
  fill: true,
});

new Zdog.Dragger({
  startElement: illo.element,
  onDragMove: function (pointer, moveX, moveY) {
    // zoom 보정
    draggableShape.translate.x += moveX / illo.zoom;
    draggableShape.translate.y += moveY / illo.zoom;
  },
});

function animate() {
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();
```

## MUST

- 인터랙션 사용 시 `animate()` 루프 필수 (드래그 중 화면 갱신)
- 터치 디바이스: `touch-action: none` CSS 설정
- moveX/moveY는 px 단위 → zoom 보정 필요 시 `/ illo.zoom`
