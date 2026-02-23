/**
 * Remotion + Zdog Integration
 * Remotion 프레임에 맞춰 Zdog 씬 애니메이션
 *
 * 설치:
 *   npm install remotion zdog
 *
 * 컴포지션 설정:
 *   fps: 30, durationInFrames: 150 (5초), width: 1080, height: 1080
 */

import React, { useEffect, useRef } from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, Easing, AbsoluteFill } from 'remotion';
import Zdog from 'zdog';

// --- 상수 ---
const COLORS = {
  bg: '#1a1a2e',
  primary: '#636',
  secondary: '#E62',
  accent: '#EA0',
  highlight: '#19F',
};
const ZOOM = 6;

// --- Zdog Scene Component ---
const ZdogScene: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const illoRef = useRef<Zdog.Illustration | null>(null);
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Illustration 초기화 (한 번만)
  useEffect(() => {
    if (!canvasRef.current) return;

    const illo = new Zdog.Illustration({
      element: canvasRef.current,
      zoom: ZOOM,
      centered: true,
    });

    // --- 도형 구성 ---

    // 메인 큐브
    new Zdog.Box({
      addTo: illo,
      width: 40,
      height: 40,
      depth: 40,
      stroke: 4,
      color: COLORS.primary,
      leftFace: COLORS.secondary,
      rightFace: COLORS.accent,
      topFace: COLORS.highlight,
    });

    // 궤도 링 1
    new Zdog.Ellipse({
      addTo: illo,
      diameter: 100,
      stroke: 3,
      color: COLORS.accent,
      rotate: { x: Zdog.TAU / 6 },
    });

    // 궤도 링 2
    new Zdog.Ellipse({
      addTo: illo,
      diameter: 100,
      stroke: 3,
      color: COLORS.highlight,
      rotate: { x: -Zdog.TAU / 6, y: Zdog.TAU / 4 },
    });

    // 궤도 위 구슬들
    const orbitRadius = 50;
    for (let i = 0; i < 3; i++) {
      new Zdog.Shape({
        addTo: illo,
        stroke: 12,
        color: [COLORS.secondary, COLORS.accent, COLORS.highlight][i],
        // 위치는 animate에서 설정
      });
    }

    illoRef.current = illo;
  }, []);

  // 프레임마다 업데이트
  useEffect(() => {
    const illo = illoRef.current;
    if (!illo) return;

    // 프레임 진행률 (0 → 1)
    const progress = frame / durationInFrames;

    // --- 인트로 (0~30f): 줌 인 ---
    const introZoom = interpolate(frame, [0, 30], [0, ZOOM], {
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.back(1.5)),
    });
    illo.zoom = introZoom;

    // --- 회전 ---
    illo.rotate.y = interpolate(frame, [0, durationInFrames], [0, Zdog.TAU * 2], {
      extrapolateRight: 'clamp',
    });
    illo.rotate.x = interpolate(frame, [0, durationInFrames], [0, Zdog.TAU * 0.5], {
      extrapolateRight: 'clamp',
    });

    // --- 구슬 궤도 위치 업데이트 ---
    const orbitRadius = 50;
    const children = illo.children;
    for (let i = 3; i < 6; i++) {
      if (children[i]) {
        const angle = (progress * Zdog.TAU * 3) + (i - 3) * (Zdog.TAU / 3);
        children[i].translate.x = Math.cos(angle) * orbitRadius;
        children[i].translate.y = Math.sin(angle) * orbitRadius * 0.3;
        children[i].translate.z = Math.sin(angle) * orbitRadius;
      }
    }

    // --- 아웃로 (마지막 20f): 페이드 아웃 효과 (줌 아웃) ---
    if (frame > durationInFrames - 20) {
      const outroZoom = interpolate(
        frame,
        [durationInFrames - 20, durationInFrames],
        [ZOOM, ZOOM * 2],
        { extrapolateRight: 'clamp', easing: Easing.in(Easing.ease) }
      );
      illo.zoom = outroZoom;
    }

    illo.updateRenderGraph();
  }, [frame, durationInFrames]);

  return (
    <canvas
      ref={canvasRef}
      width={1080}
      height={1080}
      style={{ width: '100%', height: '100%' }}
    />
  );
};

// --- Remotion Composition ---
export const ZdogComposition: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <ZdogScene />
    </AbsoluteFill>
  );
};

/**
 * Root에 등록:
 *
 * import { Composition } from 'remotion';
 * import { ZdogComposition } from './ZdogComposition';
 *
 * export const RemotionRoot: React.FC = () => {
 *   return (
 *     <Composition
 *       id="ZdogScene"
 *       component={ZdogComposition}
 *       durationInFrames={150}
 *       fps={30}
 *       width={1080}
 *       height={1080}
 *     />
 *   );
 * };
 */

export default ZdogComposition;
