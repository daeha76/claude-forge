---
name: zdog-advanced
description: Zdog 고급 기법 - Z-fighting, 비균등 스케일, Zfont, Illustration 없이 렌더링
metadata:
  tags: [zdog, z-fighting, scale, zfont, advanced, workaround]
---

# Zdog Advanced

## Z-fighting (겹침 문제)

같은 Z 평면에 있는 도형들이 렌더링 순서가 프레임마다 바뀌어 깜빡이는 현상.

### 원인

Zdog는 도형 중심점의 Z좌표로 정렬한다. 두 도형의 Z가 같으면 정렬이 불안정하다.

### 해결: translate.z 분리

```js
// WRONG: 같은 Z 평면
new Zdog.Ellipse({ addTo: illo, diameter: 80, stroke: 20, color: '#636' });
new Zdog.Rect({ addTo: illo, width: 40, height: 40, stroke: 10, color: '#E62' }); // Z-fighting!

// CORRECT: Z축 최소 분리
new Zdog.Ellipse({ addTo: illo, diameter: 80, stroke: 20, color: '#636' });
new Zdog.Rect({ addTo: illo, width: 40, height: 40, stroke: 10, color: '#E62', translate: { z: 1 } });
```

### 규칙

- 같은 부모의 겹치는 도형 → `translate.z`로 최소 1 분리
- 눈/코/입 등 얼굴 위 요소 → z: 1~5씩 오프셋
- Group의 `updateSort: true` 사용 시 동적 정렬 가능하나 성능 비용

## 비균등 스케일 버그

Zdog의 stroke는 균등 스케일만 지원한다. 비균등 스케일 시 stroke가 왜곡된다.

```js
// WRONG: stroke 왜곡
shape.scale = { x: 2, y: 1, z: 1 };

// CORRECT: 균등 스케일
shape.scale = 2;
// 또는
shape.scale = { x: 2, y: 2, z: 2 };
```

### 비균등 스케일이 필요할 때

도형 자체의 크기를 다르게 설정하여 우회:
```js
// 넓은 타원이 필요할 때
// WRONG
new Zdog.Ellipse({ addTo: illo, diameter: 80, scale: { x: 2, y: 1 } });

// CORRECT
new Zdog.Ellipse({ addTo: illo, width: 160, height: 80, stroke: 20, color: '#636' });
```

## 1px 갭 (Gap) 문제

인접한 도형 사이에 미세한 1px 간격이 보이는 현상. Canvas 안티앨리어싱 때문.

### 해결: 약간 겹치기

```js
// 몸통과 머리가 1px 벌어짐
new Zdog.Ellipse({ addTo: body, diameter: 60, translate: { y: -50 } }); // 머리

// 해결: 1~2px 겹치게 조정
new Zdog.Ellipse({ addTo: body, diameter: 60, translate: { y: -48 } }); // 머리 (2px 겹침)
```

### 또는 stroke로 가리기

```js
// 연결부에 stroke 두꺼운 도형 추가
new Zdog.Ellipse({
  addTo: body,
  diameter: 30,
  stroke: 10,      // 두꺼운 stroke가 갭을 덮음
  translate: { y: -40 },
  color: '#636',
});
```

## Zfont 연동 (텍스트)

Zdog에 텍스트를 추가하는 서드파티 플러그인.

```bash
npm install zfont
```

```js
import Zdog from 'zdog';
import 'zfont';

// 폰트 등록
Zdog.Font.register('myFont', '/fonts/MyFont.ttf');

// 또는 Google Fonts
const font = new Zdog.Font({
  src: 'https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Me5g.ttf',
});

// 텍스트 도형
new Zdog.Text({
  addTo: illo,
  font: font,
  value: 'Hello',
  fontSize: 40,
  color: '#636',
  stroke: 2,
  fill: true,
  textAlign: 'center',
  textBaseline: 'middle',
});
```

### Zfont 프로퍼티

| 프로퍼티 | 타입 | 설명 |
|----------|------|------|
| font | Zdog.Font | 폰트 인스턴스 |
| value | String | 텍스트 내용 |
| fontSize | Number | 글자 크기 |
| textAlign | String | 정렬: 'left', 'center', 'right' |
| textBaseline | String | 기준선: 'top', 'middle', 'bottom' |

### MCP 연동

```
context7 → resolve-library-id: "jaames/zfont"
→ query-docs: Zfont API 문서 조회
```

## Illustration 없이 렌더링

여러 씬을 한 캔버스에 그리거나 커스텀 후처리가 필요할 때.

```js
const scene = new Zdog.Anchor();
new Zdog.Ellipse({ addTo: scene, diameter: 80, stroke: 20, color: '#636' });

const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');

function render() {
  // 1. 그래프 업데이트 (좌표 계산)
  scene.updateGraph();

  // 2. 캔버스 초기화
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 3. 변환 적용
  ctx.save();
  ctx.translate(canvas.width / 2, canvas.height / 2);
  ctx.scale(4, 4); // zoom

  // 4. 렌더
  scene.renderGraphCanvas(ctx);
  ctx.restore();
}

function animate() {
  scene.rotate.y += 0.03;
  render();
  requestAnimationFrame(animate);
}
animate();
```

### 멀티 씬 패턴

```js
const scene1 = new Zdog.Anchor();
const scene2 = new Zdog.Anchor();

function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 씬 1: 왼쪽
  ctx.save();
  ctx.translate(120, 240);
  ctx.scale(2, 2);
  scene1.updateGraph();
  scene1.renderGraphCanvas(ctx);
  ctx.restore();

  // 씬 2: 오른쪽
  ctx.save();
  ctx.translate(360, 240);
  ctx.scale(2, 2);
  scene2.updateGraph();
  scene2.renderGraphCanvas(ctx);
  ctx.restore();
}
```

## 복제 심화 (copyGraph 활용)

### 대칭 캐릭터 패턴

```js
// 왼쪽 팔 정의
const leftArm = new Zdog.Anchor({
  addTo: body,
  translate: { x: -50, y: -10 },
});
new Zdog.Shape({
  addTo: leftArm,
  path: [{ y: 0 }, { y: 60 }],
  stroke: 16,
  color: '#636',
});

// 오른쪽 팔 = 왼쪽 미러 복제
leftArm.copyGraph({
  translate: { x: 50, y: -10 },
  scale: { x: -1 },  // X축 미러 (균등 스케일 아님 주의: 단순 좌우반전은 OK)
});
```

### MUST (copyGraph 미러)

- `scale: { x: -1 }` 좌우 미러는 예외적으로 허용 (stroke 왜곡 미미)
- 미러 복제 시 backface 방향이 반전됨 → backface 설정 확인

## 성능 팁

| 기법 | 설명 |
|------|------|
| 도형 수 최소화 | 100개 이하 권장 (모바일 60fps) |
| updateSort 최소화 | 필요한 Group에만 적용 |
| visible 토글 | 화면 밖 도형은 `visible: false` |
| 정적 씬 | 애니메이션 없으면 `updateRenderGraph` 한 번만 |
| Canvas 선호 | SVG보다 많은 도형에서 빠름 |
