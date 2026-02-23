---
name: zdog-canvas-vs-svg
description: Zdog 렌더러 선택 - Canvas vs SVG 비교, resize, zoom
metadata:
  tags: [zdog, canvas, svg, renderer, resize, zoom]
---

# Canvas vs SVG

## 선택 기준표

| 기준 | Canvas | SVG |
|------|--------|-----|
| 성능 | 빠름 (많은 도형) | 느림 (DOM 조작) |
| 해상도 | 비트맵 (Retina 처리 필요) | 벡터 (자동 선명) |
| 이벤트 | element 전체에만 | 개별 요소 이벤트 가능 |
| 접근성 | 낮음 | 높음 (DOM 구조) |
| 애니메이션 | 적합 | 도형 적으면 OK |
| 내보내기 | toDataURL() | SVG 소스 추출 |
| Remotion 연동 | 적합 | 가능 |

### 권장

- **대부분의 경우 Canvas** → 성능 좋고 Zdog 기본 타겟
- **SVG 선택 시점**: 접근성 필요, SVG 내보내기 필요, 개별 요소 이벤트 필요

## Canvas 렌더러

```html
<canvas class="zdog-canvas" width="480" height="480"></canvas>
```

```js
const illo = new Zdog.Illustration({
  element: '.zdog-canvas',  // <canvas> 요소
  zoom: 4,
});
```

### Retina 대응

Zdog는 자동 Retina 처리하지 않는다. 직접 처리:

```js
const canvas = document.querySelector('.zdog-canvas');
const ctx = canvas.getContext('2d');
const dpr = window.devicePixelRatio || 1;

canvas.width = 480 * dpr;
canvas.height = 480 * dpr;
canvas.style.width = '480px';
canvas.style.height = '480px';
ctx.scale(dpr, dpr);

const illo = new Zdog.Illustration({
  element: canvas,
  zoom: 4,
});
```

## SVG 렌더러

```html
<svg class="zdog-svg" width="480" height="480"></svg>
```

```js
const illo = new Zdog.Illustration({
  element: '.zdog-svg',  // <svg> 요소
  zoom: 4,
});
```

### SVG 장점

- 자동 Retina (벡터)
- DOM 접근 가능 (CSS 스타일링, 접근성)
- SVG 소스 추출 가능

## zoom

씬 전체 확대/축소. translate/stroke 모두에 적용.

```js
const illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  zoom: 4,    // 4배 확대
});

// 동적 zoom 변경
illo.zoom = 8;
illo.updateRenderGraph();
```

### 주의

- zoom은 좌표계 전체를 스케일함
- `translate: { x: 10 }` + `zoom: 4` → 실제 40px 이동
- Dragger의 moveX/moveY는 px 기준 → zoom 보정 필요

## centered

원점을 캔버스 중앙에 배치할지 여부.

```js
const illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  centered: true,   // 기본값: 중앙
  // centered: false → 좌상단이 원점
});
```

## resize

캔버스 크기를 자동 조절.

```js
// 부모 요소에 맞춤
const illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  resize: true,
});

// 전체 화면
const illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  resize: 'fullscreen',
});
```

### onResize 콜백

```js
const illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  resize: true,
  onResize: function (width, height) {
    // 작은 쪽에 맞춰 zoom 조정
    this.zoom = Math.min(width, height) / 200;
  },
});
```

## renderGraphCanvas / renderGraphSvg (저수준)

Illustration 없이 직접 렌더링할 때 사용 (고급).

```js
// Canvas 직접 렌더링
const anchor = new Zdog.Anchor();
new Zdog.Ellipse({ addTo: anchor, diameter: 80, stroke: 20, color: '#636' });

const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');

function render() {
  anchor.updateGraph();            // 좌표 계산
  ctx.clearRect(0, 0, 480, 480);
  ctx.save();
  ctx.translate(240, 240);         // 중앙 이동
  ctx.scale(4, 4);                 // zoom
  anchor.renderGraphCanvas(ctx);   // 렌더
  ctx.restore();
}
```

### MUST

- 대부분 Illustration 사용으로 충분
- 저수준 렌더링은 특수 경우에만 (멀티 씬, 커스텀 후처리 등)
