---
name: zdog-shapes
description: Zdog 도형 API - Shape 상속 구조, 기본/고급 도형, path 커스텀
metadata:
  tags: [zdog, shapes, geometry, path, 3d-primitives]
---

# Zdog Shapes

## Shape 상속 구조

```
Anchor (기본 노드, 렌더링 없음)
├── Shape (path 기반 2D 도형)
│   ├── Rect
│   ├── RoundedRect
│   ├── Ellipse
│   ├── Polygon
│   └── (커스텀 path)
├── Hemisphere
├── Cone
├── Cylinder
├── Box
└── Group (자식 관리 전용)
```

## 기본 도형

### Rect

```js
new Zdog.Rect({
  addTo: illo,
  width: 80,
  height: 60,
  stroke: 10,
  color: '#E62',
  fill: true,
});
```

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| width | Number | 1 | 가로 |
| height | Number | 1 | 세로 |

### RoundedRect

```js
new Zdog.RoundedRect({
  addTo: illo,
  width: 80,
  height: 60,
  cornerRadius: 15,
  stroke: 10,
  color: '#EA0',
  fill: true,
});
```

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| width | Number | 1 | 가로 |
| height | Number | 1 | 세로 |
| cornerRadius | Number | 0.25 | 모서리 반지름 |

### Ellipse

```js
new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 10,
  color: '#636',
  fill: true,
});
```

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| diameter | Number | 1 | 원 지름 |
| width | Number | - | 타원 가로 (diameter 대신) |
| height | Number | - | 타원 세로 (diameter 대신) |
| quarters | Number | 4 | 호 범위 (1=1/4원, 2=반원, 3=3/4원) |

### Polygon

```js
new Zdog.Polygon({
  addTo: illo,
  radius: 40,
  sides: 6,
  stroke: 10,
  color: '#C25',
  fill: true,
});
```

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| radius | Number | 0.5 | 외접원 반지름 |
| sides | Number | 3 | 변의 수 |

## 3D 프리미티브

### Hemisphere

```js
new Zdog.Hemisphere({
  addTo: illo,
  diameter: 80,
  stroke: false,
  color: '#C25',
  backface: '#EA0',
});
```

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| diameter | Number | 1 | 반구 지름 |
| backface | String/Boolean | true | 뒤쪽 면 색상 |

### Cone

```js
new Zdog.Cone({
  addTo: illo,
  diameter: 70,
  length: 90,
  stroke: false,
  color: '#636',
  backface: '#EA0',
});
```

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| diameter | Number | 1 | 밑면 지름 |
| length | Number | 1 | 높이 |

### Cylinder

```js
new Zdog.Cylinder({
  addTo: illo,
  diameter: 80,
  length: 120,
  stroke: false,
  color: '#C25',
  frontFace: '#EA0',
  backface: '#636',
});
```

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| diameter | Number | 1 | 원통 지름 |
| length | Number | 1 | 길이 |
| frontFace | String/Boolean | - | 앞면 색상 |

### Box

```js
new Zdog.Box({
  addTo: illo,
  width: 80,
  height: 60,
  depth: 40,
  stroke: false,
  color: '#C25',
  leftFace: '#EA0',
  rightFace: '#E62',
  topFace: '#ED0',
  bottomFace: '#636',
  frontFace: '#C25',
  rearFace: '#AAB',
});
```

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| width | Number | 1 | 가로 |
| height | Number | 1 | 세로 |
| depth | Number | 1 | 깊이 |
| frontFace / rearFace / leftFace / rightFace / topFace / bottomFace | String/Boolean | - | 면별 색상 |

## 커스텀 Path

Shape의 `path` 프로퍼티로 자유 도형을 그린다.

```js
new Zdog.Shape({
  addTo: illo,
  path: [
    { x: -32, y: -40 },              // 시작점 (line)
    { x:  32, y: -40 },              // line
    { arc: [
      { x:  48, y: -40 },            // 제어점
      { x:  48, y: -24 },            // 끝점
    ]},
    { bezier: [
      { x: 48, y: 48 },              // cp1
      { x: -48, y: 48 },             // cp2
      { x: -48, y: -24 },            // 끝점
    ]},
  ],
  closed: true,
  stroke: 10,
  color: '#636',
  fill: true,
});
```

### Path 명령어

| 명령 | 형태 | 설명 |
|------|------|------|
| line (기본) | `{ x, y, z }` | 직선 |
| move | `{ move: { x, y, z } }` | 펜 이동 (그리지 않음) |
| arc | `{ arc: [controlPoint, endPoint] }` | 2차 베지어 호 |
| bezier | `{ bezier: [cp1, cp2, endPoint] }` | 3차 베지어 곡선 |

### MUST

- path 첫 번째 요소는 항상 `{ x, y, z }` 형태 (시작점)
- `closed: true`를 써야 도형이 닫힘
- 좌표 생략 시 기본값 0 (`{ x: 10 }` = `{ x: 10, y: 0, z: 0 }`)

## 공통 프로퍼티 (모든 Shape)

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| addTo | Anchor | - | 부모 노드 (MUST) |
| color | String | '#333' | 선/면 색상 |
| stroke | Number/Boolean | 1 | 선 두께. false=0 |
| fill | Boolean | false | 면 채우기 |
| closed | Boolean | true | path 닫기 |
| visible | Boolean | true | 표시 여부 |
| backface | String/Boolean | true | 뒤집힌 면 색상/표시 |
| front | Vector | {z: 1} | 앞면 방향 벡터 |
| translate | Vector | {0,0,0} | 위치 이동 |
| rotate | Vector | {0,0,0} | 회전 (라디안) |
| scale | Number/Vector | 1 | 균등 스케일만 권장 |
