---
name: zdog-api-cheatsheet
description: Zdog 전체 API 빠른 참조표 - 클래스별 프로퍼티/메서드
metadata:
  tags: [zdog, api, reference, cheatsheet]
---

# Zdog API Cheatsheet

## 설치

```bash
npm install zdog
# CDN
# <script src="https://unpkg.com/zdog@1/dist/zdog.dist.min.js"></script>
```

## 전역 상수/유틸

| 이름 | 값 | 설명 |
|------|---|------|
| `Zdog.TAU` | `Math.PI * 2` | 360도 (라디안) |
| `Zdog.easeInOut(t)` | - | sine easeInOut (0→1) |
| `Zdog.lerp(a, b, t)` | - | 선형 보간 |
| `Zdog.modulo(a, b)` | - | 항상 양수인 나머지 |

## Vector

```js
const v = new Zdog.Vector({ x: 1, y: 2, z: 3 });
```

| 메서드 | 설명 |
|--------|------|
| `set({ x, y, z })` | 값 설정 |
| `add(v)` | 벡터 덧셈 (mutation) |
| `subtract(v)` | 벡터 뺄셈 |
| `multiply(v)` | 스칼라/벡터 곱 |
| `rotate(rotation)` | 회전 적용 |
| `magnitude()` | 크기 (길이) |
| `lerp(v, t)` | 보간 |
| `copy()` | 복제 |

## Anchor (기본 노드)

모든 Zdog 객체의 베이스 클래스.

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| addTo | Anchor | - | 부모 노드 |
| translate | Vector | {0,0,0} | 위치 |
| rotate | Vector | {0,0,0} | 회전 (라디안) |
| scale | Number/Vector | 1 | 스케일 (균등 권장) |

| 메서드 | 설명 |
|--------|------|
| `copy(options)` | 단일 노드 복제 |
| `copyGraph(options)` | 서브트리 전체 복제 |
| `addChild(child)` | 자식 추가 |
| `removeChild(child)` | 자식 제거 |
| `remove()` | 부모에서 자신 제거 |
| `updateGraph()` | 좌표 계산 (Illustration 내부 호출) |
| `renderGraphCanvas(ctx)` | Canvas에 렌더 |
| `renderGraphSvg(svg)` | SVG에 렌더 |
| `normalizeRotate()` | 회전값 정규화 |

## Shape (2D 도형)

Anchor 상속 + path 기반 렌더링.

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| path | Array | [{x:0,y:0}] | 경로 정의 |
| color | String | '#333' | 색상 |
| stroke | Number/Boolean | 1 | 선 두께 |
| fill | Boolean | false | 면 채우기 |
| closed | Boolean | true | 경로 닫기 |
| visible | Boolean | true | 표시 여부 |
| backface | String/Boolean | true | 뒷면 색상/표시 |
| front | Vector | {z:1} | 앞면 방향 |

## Rect

| 프로퍼티 | 타입 | 기본값 |
|----------|------|--------|
| width | Number | 1 |
| height | Number | 1 |

## RoundedRect

| 프로퍼티 | 타입 | 기본값 |
|----------|------|--------|
| width | Number | 1 |
| height | Number | 1 |
| cornerRadius | Number | 0.25 |

## Ellipse

| 프로퍼티 | 타입 | 기본값 |
|----------|------|--------|
| diameter | Number | 1 |
| width | Number | - |
| height | Number | - |
| quarters | Number | 4 |

## Polygon

| 프로퍼티 | 타입 | 기본값 |
|----------|------|--------|
| radius | Number | 0.5 |
| sides | Number | 3 |

## Hemisphere

| 프로퍼티 | 타입 | 기본값 |
|----------|------|--------|
| diameter | Number | 1 |
| backface | String/Boolean | true |

## Cone

| 프로퍼티 | 타입 | 기본값 |
|----------|------|--------|
| diameter | Number | 1 |
| length | Number | 1 |

## Cylinder

| 프로퍼티 | 타입 | 기본값 |
|----------|------|--------|
| diameter | Number | 1 |
| length | Number | 1 |
| frontFace | String/Boolean | - |

## Box

| 프로퍼티 | 타입 | 기본값 |
|----------|------|--------|
| width | Number | 1 |
| height | Number | 1 |
| depth | Number | 1 |
| frontFace | String/Boolean | - |
| rearFace | String/Boolean | - |
| leftFace | String/Boolean | - |
| rightFace | String/Boolean | - |
| topFace | String/Boolean | - |
| bottomFace | String/Boolean | - |

## Group

Anchor 상속 + 자식 관리.

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| updateSort | Boolean | false | Z-정렬 매 프레임 갱신 |
| visible | Boolean | true | 그룹 표시/숨김 |

## Illustration

최상위 씬 객체.

| 프로퍼티 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| element | String/Element | - | 대상 canvas/svg (MUST) |
| zoom | Number | 1 | 확대 배율 |
| centered | Boolean | true | 원점 중앙 |
| dragRotate | Boolean | false | 드래그 회전 |
| resize | Boolean/String | false | 리사이즈 |
| onResize | Function | - | 리사이즈 콜백 |
| onDragStart | Function | - | 드래그 시작 |
| onDragMove | Function | - | 드래그 중 |
| onDragEnd | Function | - | 드래그 종료 |
| onPrerender | Function | - | 렌더 직전 |

| 메서드 | 설명 |
|--------|------|
| `updateRenderGraph()` | 좌표 계산 + 렌더링 (MUST 매 프레임) |
| `setSize(w, h)` | 캔버스 크기 설정 |

## Dragger

인터랙션 핸들러.

| 프로퍼티 | 타입 | 설명 |
|----------|------|------|
| startElement | Element | 드래그 시작 감지 요소 |
| onDragStart | Function(pointer, moveX, moveY) | 시작 콜백 |
| onDragMove | Function(pointer, moveX, moveY) | 이동 콜백 |
| onDragEnd | Function() | 종료 콜백 |

## Path 명령어

| 명령 | 형태 | 설명 |
|------|------|------|
| line | `{ x, y, z }` | 직선 |
| move | `{ move: { x, y, z } }` | 펜 이동 |
| arc | `{ arc: [control, end] }` | 2차 베지어 |
| bezier | `{ bezier: [cp1, cp2, end] }` | 3차 베지어 |

## 좌표계

```
     -Y (위)
      |
      |
-X ───┼─── +X (오른쪽)
      |
      |
     +Y (아래)

+Z: 화면 쪽 (앞)
-Z: 화면 뒤 (뒤)
```

## 빠른 레시피

### 원
```js
new Zdog.Ellipse({ addTo: illo, diameter: 80, stroke: 20, color: '#636' });
```

### 점 (dot)
```js
new Zdog.Shape({ addTo: illo, stroke: 20, color: '#636' });
```

### 선
```js
new Zdog.Shape({ addTo: illo, path: [{ x: -40 }, { x: 40 }], stroke: 8, color: '#636' });
```

### 구 (sphere 근사)
```js
// Zdog에는 완전한 구가 없음. 반구 2개로 근사.
const sphere = new Zdog.Anchor({ addTo: illo });
new Zdog.Hemisphere({ addTo: sphere, diameter: 80, stroke: false, color: '#636' });
new Zdog.Hemisphere({ addTo: sphere, diameter: 80, stroke: false, color: '#636', rotate: { y: Zdog.TAU / 2 } });
```

### 링 (도넛)
```js
new Zdog.Ellipse({ addTo: illo, diameter: 80, stroke: 20, color: '#636', fill: false });
```
