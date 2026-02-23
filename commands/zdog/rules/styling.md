---
name: zdog-styling
description: Zdog 스타일링 - color, stroke, fill, backface, front 벡터
metadata:
  tags: [zdog, styling, color, stroke, fill, backface]
---

# Zdog Styling

## color

모든 도형의 색상. CSS 색상 문자열만 허용.

```js
new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: '#636',       // hex
  // color: '#663366',  // 6자리 hex
  // color: 'rgb(102,51,102)',  // rgb
  // color: 'salmon',   // 이름
  // color: 'hsla(270,50%,30%,0.8)',  // hsla
});
```

### MUST

- 문자열만 허용. 숫자 `0xFF0000` 등 사용 불가
- `rgba()` / `hsla()` 반투명 가능하나, Z-정렬 문제 발생 가능

## stroke

선(외곽선) 두께. Zdog의 핵심 렌더링 요소.

```js
// 두꺼운 선 (기본 스타일)
new Zdog.Shape({
  addTo: illo,
  path: [{ x: -40 }, { x: 40 }],
  stroke: 20,       // 20px 두께
  color: '#636',
});

// 면만 (3D 프리미티브용)
new Zdog.Box({
  addTo: illo,
  width: 80, height: 60, depth: 40,
  stroke: false,     // 선 없음
  color: '#C25',
});
```

| 값 | 동작 |
|----|------|
| Number (양수) | 해당 두께의 둥근 선 |
| false / 0 | 선 없음 (fill 또는 3D 프리미티브에 사용) |
| 1 (기본값) | 최소 두께 |

### MUST

- `stroke: 0`인 2D Shape는 보이지 않음 (fill: true여도 1px 이상 필요)
- 3D 프리미티브(Box, Cylinder 등)는 `stroke: false` 사용 가능

## fill

2D 도형의 면 채우기.

```js
// fill 없음 (선만)
new Zdog.Rect({
  addTo: illo,
  width: 80, height: 60,
  stroke: 10,
  color: '#E62',
  fill: false,   // 기본값
});

// fill 있음 (선 + 면)
new Zdog.Rect({
  addTo: illo,
  width: 80, height: 60,
  stroke: 10,
  color: '#E62',
  fill: true,    // 면 채움
});
```

### fill + stroke 조합

| stroke | fill | 결과 |
|--------|------|------|
| 20 | false | 두꺼운 윤곽선만 |
| 20 | true | 두꺼운 윤곽선 + 안쪽 면 채움 |
| 1 | true | 얇은 윤곽선 + 면 채움 |
| false | true | 면만 (2D Shape에서는 비추천) |

## closed

path 도형의 닫힘 여부.

```js
// 닫힌 삼각형
new Zdog.Shape({
  addTo: illo,
  path: [
    { x: 0, y: -40 },
    { x: 40, y: 40 },
    { x: -40, y: 40 },
  ],
  closed: true,   // 기본값: true
  stroke: 10,
  color: '#E62',
  fill: true,
});

// 열린 경로 (V자)
new Zdog.Shape({
  addTo: illo,
  path: [
    { x: -40, y: -20 },
    { x: 0, y: 20 },
    { x: 40, y: -20 },
  ],
  closed: false,
  stroke: 10,
  color: '#636',
});
```

## visible

도형 표시/숨김 토글.

```js
const shape = new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: '#636',
  visible: true,   // 기본값
});

// 토글
shape.visible = false; // 숨김
shape.visible = true;  // 표시
```

## backface

뒤집힌 면의 표시/색상 제어. 카드 뒤집기, 양면 도형에 활용.

```js
// 뒤집히면 다른 색상
new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: '#636',       // 앞면 색상
  backface: '#EA0',    // 뒷면 색상 (문자열)
});

// 뒤집히면 숨김
new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: '#636',
  backface: false,     // 뒷면 숨김
});

// 기본: 앞뒤 동일
new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: '#636',
  backface: true,      // 기본값: 앞면과 동일 색상
});
```

| 값 | 동작 |
|----|------|
| true (기본) | 앞면과 동일 색상 |
| false | 뒷면 숨김 |
| '#color' | 뒷면 지정 색상 |

## front 벡터

도형의 "앞면" 방향을 정의. backface 판정 기준.

```js
new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: '#636',
  backface: '#EA0',
  front: { z: 1 },    // 기본값: Z축 양방향이 앞
});

// 위를 앞면으로
new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: '#636',
  front: { y: -1 },   // Y축 음방향이 앞
});
```

## Box 면별 색상

```js
new Zdog.Box({
  addTo: illo,
  width: 80, height: 60, depth: 40,
  stroke: false,
  color: '#C25',          // 기본 색상 (지정 안 한 면)
  frontFace: '#E62',      // 앞면
  rearFace: '#636',       // 뒷면
  leftFace: '#EA0',       // 왼쪽
  rightFace: '#ED0',      // 오른쪽
  topFace: '#C25',        // 위
  bottomFace: '#AAB',     // 아래
});
```

| 프로퍼티 | 타입 | 설명 |
|----------|------|------|
| frontFace | String/Boolean | 앞면 (+Z) |
| rearFace | String/Boolean | 뒷면 (-Z) |
| leftFace | String/Boolean | 왼쪽 (-X) |
| rightFace | String/Boolean | 오른쪽 (+X) |
| topFace | String/Boolean | 위 (-Y) |
| bottomFace | String/Boolean | 아래 (+Y) |

### MUST

- `false`로 설정하면 해당 면 숨김 (투명 상자 가능)
- 미지정 면은 `color` 값 사용
