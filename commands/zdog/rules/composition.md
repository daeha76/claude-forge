---
name: zdog-composition
description: Zdog 씬 구성 - Illustration, Anchor 계층, Group, 복제 패턴
metadata:
  tags: [zdog, scene, illustration, anchor, group, hierarchy]
---

# Zdog Composition

## Illustration (씬 루트)

모든 Zdog 씬의 최상위 객체. Canvas 또는 SVG 요소에 바인딩한다.

```js
const illo = new Zdog.Illustration({
  element: '.zdog-canvas',  // CSS 셀렉터 또는 DOM 요소
  zoom: 4,                  // 확대 배율
  centered: true,           // 원점을 캔버스 중앙에 (기본: true)
  dragRotate: true,         // 드래그 회전 활성화
  resize: true,             // 리사이즈 반응
  onResize: function (width, height) {
    this.zoom = Math.min(width, height) / 200;
  },
});
```

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| element | String/Element | - | 대상 canvas/svg (MUST) |
| zoom | Number | 1 | 확대 배율 |
| centered | Boolean | true | 원점 중앙 배치 |
| dragRotate | Boolean | false | 드래그 회전 |
| resize | Boolean/String | false | 리사이즈. 'fullscreen' 가능 |
| onResize | Function | - | 리사이즈 콜백 |
| onDragStart | Function | - | 드래그 시작 콜백 |
| onDragMove | Function | - | 드래그 중 콜백 |
| onDragEnd | Function | - | 드래그 종료 콜백 |
| onPrerender | Function | - | 렌더 직전 콜백 |

## Anchor (빈 노드)

렌더링 없는 구조용 노드. 자식 그룹의 위치/회전 기준점 역할.

```js
const armPivot = new Zdog.Anchor({
  addTo: body,
  translate: { x: -40, y: -20 },
});

// armPivot 기준으로 회전하는 팔
new Zdog.Shape({
  addTo: armPivot,
  path: [{ y: 0 }, { y: 60 }],
  stroke: 16,
  color: '#636',
});
```

### 계층 패턴

```
Illustration (illo)
├── Anchor (body)
│   ├── Ellipse (torso)
│   ├── Anchor (leftArmPivot)
│   │   └── Shape (leftArm)
│   ├── Anchor (rightArmPivot)
│   │   └── Shape (rightArm)
│   └── Anchor (headPivot)
│       ├── Ellipse (head)
│       ├── Ellipse (leftEye)
│       └── Shape (mouth)
└── Anchor (ground)
    └── Ellipse (shadow)
```

### MUST

- 관절/피벗 포인트에는 항상 Anchor 사용
- 부모 회전이 자식에 전파됨 (의도적으로 활용)
- Anchor 자체는 렌더링 비용 없음 → 자유롭게 사용

## Group

자식 관리 전용. Anchor와 유사하지만 `visible`, `updateSort` 등 그룹 제어 기능 포함.

```js
const group = new Zdog.Group({
  addTo: illo,
  translate: { y: -20 },
  updateSort: true, // 자식 Z-정렬 활성화
});

new Zdog.Rect({ addTo: group, width: 40, height: 40, stroke: 5, color: '#E62', fill: true });
new Zdog.Ellipse({ addTo: group, diameter: 40, stroke: 5, color: '#636', fill: true, translate: { z: 20 } });
```

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| updateSort | Boolean | false | 자식 Z-정렬 매 프레임 갱신 |
| visible | Boolean | true | 그룹 전체 표시/숨김 |

### updateSort 주의

- `true`로 설정하면 매 프레임 자식 정렬 → 성능 영향
- 자식이 Z축으로 겹칠 때만 사용
- 정적 씬이면 false 유지

## addTo 패턴

모든 Zdog 객체는 `addTo`로 부모에 연결해야 씬에 포함된다.

```js
// CORRECT
new Zdog.Ellipse({
  addTo: illo,    // 씬에 추가됨
  diameter: 80,
  stroke: 20,
  color: '#636',
});

// WRONG - addTo 누락
const orphan = new Zdog.Ellipse({
  diameter: 80,
  stroke: 20,
  color: '#636',
});
// orphan은 렌더링되지 않음
```

## 복제 (copy / copyGraph)

### copy() - 단일 객체 복제

```js
const original = new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: '#636',
});

// 프로퍼티 오버라이드 가능
const clone = original.copy({
  translate: { x: 100 },
  color: '#E62',
});
```

### copyGraph() - 자식 포함 전체 복제

```js
const arm = new Zdog.Anchor({ addTo: body, translate: { x: -40 } });
new Zdog.Shape({ addTo: arm, path: [{ y: 0 }, { y: 60 }], stroke: 16, color: '#636' });
new Zdog.Ellipse({ addTo: arm, diameter: 16, translate: { y: 68 }, stroke: 8, color: '#EA0' });

// 전체 서브트리 복제 (arm + 자식 모두)
const rightArm = arm.copyGraph({
  translate: { x: 40 },
});
```

### MUST

- `copy()`는 자식을 복제하지 않음 (단일 노드만)
- `copyGraph()`는 전체 서브트리 깊은 복제
- 복제된 객체의 `addTo`는 원본과 동일한 부모 (오버라이드 가능)
- 캐릭터 좌우 대칭에 `copyGraph` + `scale: { x: -1 }` 패턴 활용

## updateRenderGraph

```js
// 매 프레임 호출 (MUST)
illo.updateRenderGraph();

// 정적 씬이면 한 번만
illo.updateRenderGraph();
```

### 동작 원리

1. 씬 트리를 순회하며 월드 좌표 계산
2. Z-정렬 (뒤→앞)
3. 렌더링 (Canvas drawPath 또는 SVG DOM 갱신)

## 씬 초기화 패턴

```js
// 1. Illustration 생성
const illo = new Zdog.Illustration({ element: '.zdog-canvas', zoom: 4, dragRotate: true });

// 2. 도형 추가 (addTo 체인)
const body = new Zdog.Anchor({ addTo: illo });
new Zdog.Ellipse({ addTo: body, diameter: 80, stroke: 20, color: '#636' });

// 3. 애니메이션 루프 (또는 정적이면 updateRenderGraph 한 번)
function animate() {
  illo.rotate.y += 0.03;
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();
```
