/**
 * Zdog Character Assembly
 * Anchor 계층으로 머리/몸/팔/다리 조립 + 관절 회전 애니메이션
 *
 * HTML: <canvas class="zdog-canvas" width="480" height="480"></canvas>
 */

import Zdog from 'zdog';

// --- 상수 ---
const COLORS = {
  skin: '#FFCC99',
  body: '#636',
  eye: '#333',
  mouth: '#E62',
  shoe: '#333',
};
const ZOOM = 3;
const WALK_SPEED = 0.06;

// --- Illustration ---
const illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  zoom: ZOOM,
  dragRotate: true,
});

// --- Body (기준점) ---
const body = new Zdog.Anchor({
  addTo: illo,
});

// 몸통
new Zdog.RoundedRect({
  addTo: body,
  width: 50,
  height: 70,
  cornerRadius: 15,
  stroke: 20,
  color: COLORS.body,
  fill: true,
});

// --- Head ---
const headPivot = new Zdog.Anchor({
  addTo: body,
  translate: { y: -65 },
});

// 머리
new Zdog.Ellipse({
  addTo: headPivot,
  diameter: 50,
  stroke: 30,
  color: COLORS.skin,
});

// 왼쪽 눈
new Zdog.Ellipse({
  addTo: headPivot,
  diameter: 6,
  stroke: 4,
  color: COLORS.eye,
  translate: { x: -10, z: 15 },
});

// 오른쪽 눈
new Zdog.Ellipse({
  addTo: headPivot,
  diameter: 6,
  stroke: 4,
  color: COLORS.eye,
  translate: { x: 10, z: 15 },
});

// 입
new Zdog.Ellipse({
  addTo: headPivot,
  diameter: 10,
  quarters: 2,
  stroke: 3,
  color: COLORS.mouth,
  translate: { y: 8, z: 14 },
  rotate: { z: Zdog.TAU / 4 }, // 반원을 아래로
});

// --- Left Arm ---
const leftArmPivot = new Zdog.Anchor({
  addTo: body,
  translate: { x: -38, y: -20 },
});

new Zdog.Shape({
  addTo: leftArmPivot,
  path: [{ y: 0 }, { y: 50 }],
  stroke: 16,
  color: COLORS.body,
});

// 왼손
new Zdog.Ellipse({
  addTo: leftArmPivot,
  diameter: 10,
  stroke: 12,
  color: COLORS.skin,
  translate: { y: 56 },
});

// --- Right Arm (미러 복제) ---
const rightArmPivot = leftArmPivot.copyGraph({
  translate: { x: 38, y: -20 },
});

// --- Left Leg ---
const leftLegPivot = new Zdog.Anchor({
  addTo: body,
  translate: { x: -14, y: 28 },
});

new Zdog.Shape({
  addTo: leftLegPivot,
  path: [{ y: 0 }, { y: 50 }],
  stroke: 16,
  color: COLORS.body,
});

// 왼쪽 신발
new Zdog.RoundedRect({
  addTo: leftLegPivot,
  width: 18,
  height: 10,
  cornerRadius: 4,
  stroke: 10,
  color: COLORS.shoe,
  fill: true,
  translate: { y: 58, z: 4 },
  rotate: { x: Zdog.TAU / 4 },
});

// --- Right Leg (미러 복제) ---
const rightLegPivot = leftLegPivot.copyGraph({
  translate: { x: 14, y: 28 },
});

// --- Walk Animation ---
let t = 0;

function animate() {
  t += WALK_SPEED;

  // 팔 흔들기 (반대 방향)
  leftArmPivot.rotate.x = Math.sin(t) * 0.6;
  rightArmPivot.rotate.x = Math.sin(t + Math.PI) * 0.6;

  // 다리 흔들기
  leftLegPivot.rotate.x = Math.sin(t + Math.PI) * 0.4;
  rightLegPivot.rotate.x = Math.sin(t) * 0.4;

  // 머리 살짝 좌우 흔들기
  headPivot.rotate.z = Math.sin(t * 0.5) * 0.05;

  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}

animate();
