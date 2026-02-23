---
name: zdog-known-issues
description: Zdog v1 베타 한계, 알려진 버그, 우회법
metadata:
  tags: [zdog, bugs, limitations, workaround]
---

# Zdog Known Issues

## v1 베타 상태

Zdog는 v1.1.3 이후 업데이트가 드문 상태. 핵심 기능은 안정적이나 일부 한계가 있다.

## 알려진 이슈

### 1. Z-fighting (깜빡임)

**증상**: 같은 Z 평면의 도형이 프레임마다 앞뒤가 바뀌며 깜빡임.

**원인**: 도형 중심점 기반 Z-정렬의 한계.

**우회**:
```js
// translate.z로 최소 1px 분리
shapeA.translate.z = 0;
shapeB.translate.z = 1;
```

### 2. 비균등 스케일 stroke 왜곡

**증상**: `scale: { x: 2, y: 1 }` 시 stroke가 한쪽만 두꺼워짐.

**원인**: stroke는 균등 스케일만 지원.

**우회**: 도형 자체 크기로 비율 조정.
```js
// scale 대신 width/height 직접 설정
new Zdog.Ellipse({ width: 160, height: 80 });
```

### 3. 1px 갭 (Canvas 안티앨리어싱)

**증상**: 인접 도형 사이 미세한 틈.

**우회**: 도형을 1~2px 겹치거나 두꺼운 stroke로 가리기.

### 4. 완전한 구(Sphere) 없음

**증상**: Sphere 클래스가 없음.

**우회**: Hemisphere 2개 결합.
```js
const sphere = new Zdog.Anchor({ addTo: illo });
new Zdog.Hemisphere({ addTo: sphere, diameter: 80, stroke: false, color: '#636' });
new Zdog.Hemisphere({ addTo: sphere, diameter: 80, stroke: false, color: '#636', rotate: { y: Zdog.TAU / 2 } });
```

### 5. 투명도(alpha) Z-정렬 문제

**증상**: `rgba()` 반투명 색상 사용 시 정렬이 부자연스러움.

**원인**: Z-정렬이 도형 단위(중심점 기준)이므로 반투명 겹침이 정확하지 않음.

**우회**: 가능하면 불투명 색상 사용. 반투명이 필요하면 Z 분리를 확실히.

### 6. 텍스트 미지원 (내장)

**증상**: 텍스트 렌더링 API가 없음.

**우회**: Zfont 플러그인 사용.
```bash
npm install zfont
```

### 7. 히트 테스트 / 레이캐스팅 없음

**증상**: 특정 도형 클릭 감지가 어려움.

**원인**: pseudo-3D이므로 실제 3D 히트 테스트 불가.

**우회**: Dragger로 전체 씬 드래그만 지원. 개별 도형 클릭은 2D 좌표 수동 계산 필요.

## 부적합 용도

| 용도 | 이유 | 대안 |
|------|------|------|
| 복잡한 3D 모델 | 메시/텍스처 미지원 | Three.js |
| 광원/그림자 | 조명 시스템 없음 | Three.js, Babylon.js |
| 물리 시뮬레이션 | 물리 엔진 없음 | Cannon.js + Three.js |
| 대량 도형 (500+) | 성능 저하 | Three.js (WebGL) |
| 정밀 히트 테스트 | 레이캐스팅 없음 | Three.js Raycaster |

## 적합 용도

| 용도 | 이유 |
|------|------|
| 아이콘/로고 애니메이션 | 가볍고 친근한 스타일 |
| 캐릭터 일러스트 | 둥근 stroke 기반 스타일 |
| UI 장식/위젯 | 28KB 경량, 의존성 없음 |
| 교육/설명 다이어그램 | 단순 3D로 직관적 |
| Remotion 영상 소품 | 코드 기반 3D 삽화 |
