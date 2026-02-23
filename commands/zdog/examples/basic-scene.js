/**
 * Zdog Basic Scene
 * Hello World: 원 + 사각형 + 회전 애니메이션 + 드래그 회전
 *
 * HTML: <canvas class="zdog-canvas" width="480" height="480"></canvas>
 */

import Zdog from 'zdog';

// --- 상수 ---
const CANVAS_SELECTOR = '.zdog-canvas';
const ZOOM = 4;
const ROTATION_SPEED = 0.03;
const COLORS = {
  circle: '#636',
  rect: '#E62',
  polygon: '#EA0',
};

// --- Illustration (씬 루트) ---
const illo = new Zdog.Illustration({
  element: CANVAS_SELECTOR,
  zoom: ZOOM,
  dragRotate: true, // 마우스/터치 드래그 회전
});

// --- 도형 ---

// 원
new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: COLORS.circle,
  translate: { z: 40 }, // Z-fighting 방지
});

// 사각형
new Zdog.Rect({
  addTo: illo,
  width: 60,
  height: 60,
  stroke: 10,
  color: COLORS.rect,
  fill: true,
  translate: { z: -40 },
});

// 육각형
new Zdog.Polygon({
  addTo: illo,
  radius: 30,
  sides: 6,
  stroke: 8,
  color: COLORS.polygon,
  fill: true,
  translate: { y: 60 },
});

// --- 애니메이션 ---
let isSpinning = true;

illo.onDragStart = function () {
  isSpinning = false;
};

illo.onDragEnd = function () {
  isSpinning = true;
};

function animate() {
  if (isSpinning) {
    illo.rotate.y += ROTATION_SPEED;
  }
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}

animate();
