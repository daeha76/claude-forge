/**
 * Zdog Interactive Widget
 * SVG 렌더러 + 드래그 인터랙션 + 색상 변경
 *
 * HTML: <svg class="zdog-svg" width="480" height="480"></svg>
 *       <button id="color-btn">Change Color</button>
 */

import Zdog from 'zdog';

// --- 상수 ---
const ZOOM = 4;
const PALETTE = ['#636', '#E62', '#EA0', '#C25', '#19F', '#2D6', '#F80'];
const DAMPING = 0.95;
const DRAG_SENSITIVITY = 0.004;

// --- 상태 ---
let colorIndex = 0;
let velocityY = 0;
let velocityX = 0;
let isSpinning = true;

// --- Illustration (SVG 렌더러) ---
const illo = new Zdog.Illustration({
  element: '.zdog-svg',  // SVG 요소
  zoom: ZOOM,
  resize: true,
  onResize: function (width, height) {
    this.zoom = Math.min(width, height) / 120;
  },
});

// --- 메인 도형: 둥근 큐브 ---
const cube = new Zdog.Box({
  addTo: illo,
  width: 50,
  height: 50,
  depth: 50,
  stroke: 8,
  color: PALETTE[colorIndex],
  leftFace: darken(PALETTE[colorIndex]),
  rightFace: lighten(PALETTE[colorIndex]),
  topFace: lighten(PALETTE[colorIndex]),
  bottomFace: darken(PALETTE[colorIndex]),
});

// 장식: 큐브 위 작은 구슬
new Zdog.Ellipse({
  addTo: illo,
  diameter: 15,
  stroke: 12,
  color: '#FFF',
  translate: { y: -50 },
});

// 장식: 큐브 아래 그림자
new Zdog.Ellipse({
  addTo: illo,
  diameter: 60,
  stroke: 2,
  color: 'rgba(0,0,0,0.15)',
  fill: true,
  translate: { y: 50 },
  rotate: { x: Zdog.TAU / 4 },
});

// --- 색상 유틸 ---
function darken(hex) {
  return adjustBrightness(hex, -30);
}

function lighten(hex) {
  return adjustBrightness(hex, 30);
}

function adjustBrightness(hex, amount) {
  // 간단한 밝기 조정 (3자리/6자리 hex 지원)
  const expanded = hex.length === 4
    ? '#' + hex[1] + hex[1] + hex[2] + hex[2] + hex[3] + hex[3]
    : hex;

  const num = parseInt(expanded.slice(1), 16);
  const r = Math.min(255, Math.max(0, ((num >> 16) & 0xFF) + amount));
  const g = Math.min(255, Math.max(0, ((num >> 8) & 0xFF) + amount));
  const b = Math.min(255, Math.max(0, (num & 0xFF) + amount));

  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
}

// --- 드래그 인터랙션 (관성 포함) ---
new Zdog.Dragger({
  startElement: illo.element,
  onDragStart: function () {
    isSpinning = false;
    velocityY = 0;
    velocityX = 0;
  },
  onDragMove: function (pointer, moveX, moveY) {
    // 드래그 → 회전 (관성 속도 저장)
    velocityY = moveX * DRAG_SENSITIVITY;
    velocityX = -moveY * DRAG_SENSITIVITY;
    illo.rotate.y += velocityY;
    illo.rotate.x += velocityX;
  },
  onDragEnd: function () {
    // 관성 회전 유지 (isSpinning은 false 유지)
  },
});

// --- 색상 변경 버튼 ---
const btn = document.querySelector('#color-btn');
if (btn) {
  btn.addEventListener('click', function () {
    colorIndex = (colorIndex + 1) % PALETTE.length;
    const color = PALETTE[colorIndex];
    cube.color = color;
    cube.leftFace = darken(color);
    cube.rightFace = lighten(color);
    cube.topFace = lighten(color);
    cube.bottomFace = darken(color);
    cube.frontFace = color;
    cube.rearFace = color;
  });
}

// --- 애니메이션 ---
function animate() {
  if (!isSpinning) {
    // 관성 감쇠
    illo.rotate.y += velocityY;
    illo.rotate.x += velocityX;
    velocityY *= DAMPING;
    velocityX *= DAMPING;

    // 속도가 충분히 느려지면 자동 회전 재개
    if (Math.abs(velocityY) < 0.0005 && Math.abs(velocityX) < 0.0005) {
      isSpinning = true;
    }
  } else {
    illo.rotate.y += 0.02;
  }

  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}

animate();
