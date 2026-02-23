/**
 * Zdog Logo Animation
 * 여러 도형 조합 로고 + 순차 등장 (staggered) + easeInOut
 *
 * HTML: <canvas class="zdog-canvas" width="480" height="480"></canvas>
 */

import Zdog from 'zdog';

// --- 상수 ---
const ZOOM = 3;
const STAGGER_DELAY = 12;   // 각 도형 간 프레임 지연
const ANIM_DURATION = 40;   // 등장 애니메이션 프레임 수
const ROTATION_SPEED = 0.01;
const COLORS = ['#636', '#E62', '#EA0', '#C25', '#19F'];

// --- Easing ---
function easeOutBack(t) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
}

function easeInOut(t) {
  return 0.5 - Math.cos(t * Math.PI) / 2;
}

// --- Illustration ---
const illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  zoom: ZOOM,
  dragRotate: true,
});

// --- 로고 그룹 ---
const logoGroup = new Zdog.Group({
  addTo: illo,
  updateSort: true,
});

// --- 도형 정의 ---
const shapeConfigs = [
  // 중앙 원
  {
    type: 'Ellipse',
    props: { diameter: 60, stroke: 16, color: COLORS[0], fill: true },
    targetTranslate: { x: 0, y: 0, z: 20 },
  },
  // 위쪽 삼각형
  {
    type: 'Polygon',
    props: { radius: 25, sides: 3, stroke: 10, color: COLORS[1], fill: true },
    targetTranslate: { x: 0, y: -60, z: 0 },
    targetRotate: { z: 0 },
  },
  // 오른쪽 사각형
  {
    type: 'Rect',
    props: { width: 40, height: 40, stroke: 10, color: COLORS[2], fill: true },
    targetTranslate: { x: 60, y: 0, z: -10 },
    targetRotate: { z: Zdog.TAU / 8 },
  },
  // 아래 오각형
  {
    type: 'Polygon',
    props: { radius: 25, sides: 5, stroke: 10, color: COLORS[3], fill: true },
    targetTranslate: { x: 0, y: 60, z: -20 },
  },
  // 왼쪽 다이아몬드
  {
    type: 'Rect',
    props: { width: 35, height: 35, stroke: 10, color: COLORS[4], fill: true },
    targetTranslate: { x: -60, y: 0, z: -10 },
    targetRotate: { z: Zdog.TAU / 8 },
  },
];

// --- 도형 생성 ---
const animItems = shapeConfigs.map((config, i) => {
  const shape = new Zdog[config.type]({
    addTo: logoGroup,
    ...config.props,
    translate: { x: 0, y: 0, z: 0 }, // 초기: 중앙
    scale: 0,                          // 초기: 안 보임
  });

  return {
    shape,
    delay: i * STAGGER_DELAY,
    targetTranslate: config.targetTranslate || { x: 0, y: 0, z: 0 },
    targetRotate: config.targetRotate || { x: 0, y: 0, z: 0 },
  };
});

// --- 애니메이션 ---
let frame = 0;
const totalFrames = (shapeConfigs.length - 1) * STAGGER_DELAY + ANIM_DURATION + 60;
let introComplete = false;

function animate() {
  // 등장 애니메이션
  if (!introComplete) {
    animItems.forEach(({ shape, delay, targetTranslate, targetRotate }) => {
      const localFrame = frame - delay;

      if (localFrame >= 0 && localFrame <= ANIM_DURATION) {
        const t = easeOutBack(Math.min(localFrame / ANIM_DURATION, 1));

        // 스케일 등장
        shape.scale = t;

        // 위치 이동 (중앙 → 목표)
        shape.translate.x = targetTranslate.x * easeInOut(localFrame / ANIM_DURATION);
        shape.translate.y = targetTranslate.y * easeInOut(localFrame / ANIM_DURATION);
        shape.translate.z = targetTranslate.z * easeInOut(localFrame / ANIM_DURATION);

        // 회전
        shape.rotate.z = targetRotate.z * easeInOut(localFrame / ANIM_DURATION);
      }
    });

    if (frame > totalFrames) {
      introComplete = true;
    }
    frame++;
  }

  // 지속 회전
  logoGroup.rotate.y += ROTATION_SPEED;

  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}

animate();
