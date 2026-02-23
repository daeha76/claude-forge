---
name: zdog
description: Zdog pseudo-3D 엔진 가이드 - 도형, 애니메이션, 인터랙션, Remotion 연동
metadata:
  tags: [zdog, 3d, canvas, svg, animation, pseudo-3d, illustration]
---

# Zdog Skill

28KB pseudo-3D 엔진으로 둥글고 친근한 3D 일러스트레이션을 코드로 제작한다.

## Quick Start

```bash
npm install zdog
```

```js
const illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  zoom: 4,
  dragRotate: true,
});

new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: '#636',
});

function animate() {
  illo.rotate.y += 0.03;
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();
```

## 작업별 가이드

| 작업 | 파일 | 설명 |
|------|------|------|
| 도형 만들기 | [rules/shapes.md](rules/shapes.md) | Shape 상속 구조, Rect/Ellipse/Polygon/Box 등 |
| 애니메이션 | [rules/animations.md](rules/animations.md) | 회전/이동 루프, easing, spring 패턴 |
| 씬 구성 | [rules/composition.md](rules/composition.md) | Illustration, Anchor 계층, Group, copy |
| 인터랙션 | [rules/interaction.md](rules/interaction.md) | Dragger, dragRotate, 터치/펜 지원 |
| 스타일링 | [rules/styling.md](rules/styling.md) | color, stroke, fill, backface 등 |
| 렌더러 선택 | [rules/canvas-vs-svg.md](rules/canvas-vs-svg.md) | Canvas vs SVG 비교, resize, zoom |
| 고급 기법 | [rules/advanced.md](rules/advanced.md) | Z-fighting, 복제, Zfont, 커스텀 렌더링 |

## 참조 & 예제

| 파일 | 설명 |
|------|------|
| [references/api-cheatsheet.md](references/api-cheatsheet.md) | 전체 API 빠른 참조표 |
| [references/known-issues.md](references/known-issues.md) | v1 베타 한계, 버그 우회법 |
| [examples/basic-scene.js](examples/basic-scene.js) | Hello World + 회전 |
| [examples/character.js](examples/character.js) | 캐릭터 조립 (Anchor 계층) |
| [examples/logo-animation.js](examples/logo-animation.js) | 로고 순차 등장 애니메이션 |
| [examples/interactive-widget.js](examples/interactive-widget.js) | SVG 드래그 위젯 |
| [examples/remotion-integration.tsx](examples/remotion-integration.tsx) | Remotion + Zdog 영상 |

## 연동 도구

| 도구 | 용도 |
|------|------|
| context7 (`/jaames/zfont`) | Zfont 텍스트 플러그인 문서 |
| exa | Zdog 예제/패턴 웹 검색 |
| remotion | Zdog + Remotion 영상 제작 |
| playwright | 캔버스 스크린샷/E2E 테스트 |

## MUST 규칙

1. **stroke 필수** - Zdog는 stroke 기반 엔진. `stroke: 0`이면 아무것도 안 보임
2. **updateRenderGraph** - 매 프레임 반드시 호출. 빼먹으면 화면 갱신 안 됨
3. **addTo 필수** - 모든 도형은 `addTo`로 부모에 연결. 빠뜨리면 렌더링 안 됨
4. **Z-fighting 주의** - 같은 평면의 도형은 translate.z로 최소 1px 분리
5. **비균등 스케일 금지** - `scale: { x: 2, y: 1 }` 사용 시 stroke 깨짐
6. **색상은 문자열** - `color: '#636'` (CSS 색상 문자열만 허용)

## FORBIDDEN

- `stroke: 0` (보이지 않음, 최소 `stroke: 1` 사용)
- `new Shape()` 후 `addTo` 누락 (씬에 추가되지 않음)
- 비균등 `scale` (stroke 왜곡 발생)
- `animate()` 내에서 `new Shape()` 생성 (메모리 누수)
- `updateRenderGraph()` 호출 누락 (화면 미갱신)
