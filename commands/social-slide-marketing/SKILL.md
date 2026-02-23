---
name: social-slide-marketing
description: >
  소셜 미디어 슬라이드쇼 마케팅 자동화. 6장 세로 이미지 생성(Gemini 3 Pro) →
  텍스트 오버레이 → TikTok/Instagram 게시(Postiz) → 성과 추적 → 자동 최적화.
  Use when: TikTok 마케팅, 슬라이드쇼, 소셜 미디어 자동화, 인스타 릴스,
  바이럴 콘텐츠, social media marketing, slideshow ads, TikTok growth, viral content.
---

# Social Slideshow Marketing

6장 세로 슬라이드쇼를 생성하고 TikTok/Instagram에 자동 게시하는 마케팅 자동화 스킬.

## 사용법

```bash
# 온보딩 (최초 1회)
/social-slide-marketing onboard

# 슬라이드쇼 생성 + 게시
/social-slide-marketing create "훅 텍스트 또는 주제"

# 이미지만 생성 (게시 안 함)
/social-slide-marketing create --generate-only "주제"

# 일일 분석 리포트
/social-slide-marketing report

# 경쟁사 리서치
/social-slide-marketing research "경쟁사 앱 이름"

# 설정 확인
/social-slide-marketing status
```

## 온보딩 흐름

사용자가 `/social-slide-marketing onboard`를 실행하면 아래 3단계로 진행:

### Phase 1: 앱 정보 + API 키 (5분)

대화형으로 앱/제품 정보를 수집하고 API 키를 설정한다:

**앱 정보 수집:**
1. **앱/제품 이름** (name): "어떤 앱이나 제품을 홍보하시나요?"
2. **한 줄 설명** (description): "한 줄로 설명하면?"
3. **타겟 오디언스** (audience): "누가 사용하나요? (예: 20-30대 직장인)"
4. **해결하는 문제** (problem): "어떤 문제를 해결하나요?"
5. **차별화 포인트** (differentiator): "경쟁사 대비 장점은?"
6. **앱 URL** (url): "다운로드/가입 링크는?"
7. **카테고리** (category): "어떤 카테고리? (교육/SaaS/이커머스/F&B/뷰티/피트니스/생산성/기타)"

**API 키 설정:**
- `~/.env`의 `GEMINI_API_KEY` 확인
- Postiz API Key 발급 (https://postiz.com)
- Postiz에서 TikTok/Instagram Integration ID 복사
- `~/.social-slide-marketing/config.json` 초기화

```bash
python3 ~/.claude/commands/social-slide-marketing/scripts/onboarding.py --init
python3 ~/.claude/commands/social-slide-marketing/scripts/onboarding.py --validate
```

### Phase 2: 첫 테스트 슬라이드 생성 (5분)

테스트 이미지 1장을 생성하여 스타일을 확인한다:

```bash
python3 ~/.claude/commands/social-slide-marketing/scripts/generate_slides.py \
  --test \
  --config ~/.social-slide-marketing/config.json
```

- 이미지 스타일 확인 (미니멀/볼드/일러스트 중 선택)
- 만족하면 `sceneDescription`을 config에 저장
- 텍스트 오버레이 테스트 (폰트, 크기, 위치 확인)

### Phase 3: 첫 게시 (2분)

전체 6장 슬라이드쇼를 생성하고 게시한다:

```bash
# 전체 파이프라인 테스트 (dry-run)
/social-slide-marketing create --generate-only "테스트 훅"

# 확인 후 실제 게시
/social-slide-marketing create "테스트 훅"
```

- dry-run으로 6장 슬라이드쇼 미리보기
- 만족하면 실제 게시 또는 초안 저장

---

## 선택적 설정 (첫 게시 후)

첫 게시가 완료된 후 필요에 따라 설정:

### 경쟁사 분석

```bash
python3 ~/.claude/commands/social-slide-marketing/scripts/competitor_research.py \
  --action add \
  --name "경쟁사명" \
  --url "https://tiktok.com/@경쟁사" \
  --notes "슬라이드쇼 스타일 메모"
```

- 최소 3개 경쟁사의 TikTok/Instagram 슬라이드쇼 분석
- 성공적인 훅 패턴 기록

### 콘텐츠 전략

- 초기 훅 20개 브레인스토밍
- 게시 스케줄: 하루 1-3개 (기본 07:30, 16:30, 21:00 KST)
- CTA 로테이션 (바이오 링크, 댓글 고정, DM 유도)

### 일일 분석 크론 설정

```bash
# crontab 예시 (매일 오전 9시)
0 9 * * * python3 ~/.claude/commands/social-slide-marketing/scripts/daily_report.py
```

### 전환 추적 설정

- **수동**: 바이오 링크 단축 URL (Bitly 등) → 클릭 수 확인
- **앱스토어**: 앱 다운로드 수 추적
- **웹사이트**: UTM 파라미터 + Google Analytics

### 계정 워밍업 (TikTok 신규 계정)

```
TikTok 계정 워밍업 가이드 (7-14일):
1. 하루 30분 이상 다른 영상 시청 + 좋아요/댓글
2. 3-5개 관련 계정 팔로우
3. 프로필 완성 (사진, 바이오, 링크)
4. 7일 후부터 콘텐츠 게시 시작
5. 처음 5개 영상은 가장 성공적인 훅으로 제작
```

## 슬라이드쇼 생성 워크플로우

사용자가 `/social-slide-marketing create "훅 또는 주제"`를 실행하면:

### Step 1: 훅 선택/생성

입력이 짧은 주제인 경우 → 훅 브레인스토밍 후 선택 요청
입력이 구체적 훅인 경우 → 바로 사용

성과 데이터가 있으면 `~/.social-slide-marketing/hook-rankings.json`의 공식 랭킹을 참조하여 tier1 공식 위주로 훅을 추천한다.

**훅 기준 (Tier 1 공식):**
- "I found an app that [benefit]"
- "Stop [current behavior], use [app] instead"
- "This app will [transformation] in [timeframe]"
- "[앱이름] 써봤는데 진짜 [결과]"
- "[문제] 때문에 고민이라면 이거 써보세요"

### Step 2: 6장 슬라이드 이미지 생성

```bash
python3 ~/.claude/commands/social-slide-marketing/scripts/generate_slides.py \
  --hook "선택된 훅" \
  --config ~/.social-slide-marketing/config.json \
  --output /tmp/social-slides/[timestamp]/
```

이미지 생성은 **아키텍처 락킹(Scene Locking)** 방식을 사용한다. 6장 모두 동일한 인물, 환경, 카메라 앵글을 공유하며, 슬라이드별로 감정(emotion), 분위기(mood), 색조(color grading)만 변경된다. 이를 통해 슬라이드 간 시각적 일관성을 보장하고, 각 장마다 다른 캐릭터/배경이 나오는 "AI 짜집기" 느낌을 방지한다. 장면 설정은 앱 카테고리에서 자동 생성되거나 config의 `sceneDescription` 값을 사용한다.

6장 구조:
1. **훅 슬라이드**: 주의를 끄는 첫 장 (텍스트 없는 시각적 훅)
2. **문제 제기**: 타겟이 공감하는 문제
3. **발견/소개**: 앱/제품 소개 ("이걸 발견했는데...")
4. **변환 1**: 핵심 기능/결과 시연
5. **변환 2**: 추가 기능/결과 시연
6. **CTA**: 행동 유도 ("바이오 링크 클릭" 등)

### Step 3: 텍스트 오버레이

```bash
python3 ~/.claude/commands/social-slide-marketing/scripts/add_text_overlay.py \
  --slides /tmp/social-slides/[timestamp]/ \
  --texts "슬라이드1텍스트||슬라이드2텍스트||...||슬라이드6텍스트"
```

규칙:
- 폰트 크기: 이미지 너비의 6.5%
- 위치: 상단에서 30% (안전 영역)
- 흰색 텍스트 + 검정 아웃라인 (가독성)
- 4-6단어/줄, 최대 3줄

### Step 4: 캡션 작성

스토리텔링 형식의 캡션을 작성한다:

```
[짧은 훅 반복]

[스토리 (50-100자)]

[CTA: 바이오 링크 / 댓글 / DM]

[해시태그 3-5개]
```

### Step 5: Postiz로 멀티플랫폼 게시

```bash
python3 ~/.claude/commands/social-slide-marketing/scripts/post_to_platforms.py \
  --slides /tmp/social-slides/[timestamp]/final/ \
  --caption "캡션 텍스트" \
  --title "TikTok 제목" \
  --config ~/.social-slide-marketing/config.json
```

- **TikTok**: 초안(SELF_ONLY)으로 게시 → 사용자가 트렌딩 사운드 추가 후 게시
  - `autoAddMusic: true` 설정 시 TikTok이 자동으로 사운드 추가 (사용자 작업 불필요)
  - `autoAddMusic: false` 설정 시 기존대로 수동 사운드 추가 (~60초)
- **Instagram**: 캐러셀로 직접 게시

### Step 6: 사용자 안내

```
슬라이드쇼 생성 완료!

TikTok (autoAddMusic: true 시):
  자동 게시 + 자동 사운드 추가 완료. 추가 작업 불필요.

TikTok (autoAddMusic: false 시):
1. TikTok 앱 열기
2. 초안에서 슬라이드쇼 찾기
3. 트렌딩 사운드 추가
4. 게시 버튼

Instagram: 자동 게시됨 (캐러셀)

이미지 위치: /tmp/social-slides/[timestamp]/
```

## 분석 리포트

사용자가 `/social-slide-marketing report`를 실행하면:

```bash
python3 ~/.claude/commands/social-slide-marketing/scripts/daily_report.py \
  --config ~/.social-slide-marketing/config.json
```

### 진단 프레임워크

| 조회수 | 전환 | 진단 | 조치 |
|--------|------|------|------|
| 높음 (50K+) | 높음 | SCALE IT | 동일 훅으로 변형 3개 제작, 예산 투입 |
| 높음 (50K+) | 낮음 | FIX CTA | CTA 슬라이드/캡션 변경, 바이오 링크 최적화 |
| 중간 (10K-50K) | 높음 | BOOST | 유료 프로모션 집행, 리포스트/듀엣 유도, 게시 시간 최적화 |
| 중간 (10K-50K) | 낮음 | OPTIMIZE | 훅/CTA 미세 조정, A/B 테스트 |
| 낮음 (<10K) | 높음 | FIX HOOKS | 훅 교체, 첫 장 이미지 변경 |
| 낮음 (<10K) | 낮음 | FULL RESET | 새 앵글 시도, 경쟁사 재분석 |

### 3-Layer 퍼널 진단

| 레이어 | 측정 | 소스 |
|--------|------|------|
| Views | 조회수 | Postiz API |
| Link Clicks | 링크 클릭 | Bitly/수동 입력 |
| Conversions | 전환 (다운로드/가입) | 수동 입력 |

### 리포트 내용

- 최근 3일 포스트별 성과 (조회수, 좋아요, 댓글, 공유)
- 퍼널 진단 (Views → Clicks → Conversions)
- 훅 공식 랭킹 (자동 승급/강등)
- 자동 생성 훅 변형 (실제 텍스트)
- CTA 로테이션 추천
- 학습 기록 (훅 길이, 언어, 시간대별 성과 패턴)

## 옵션 처리

| 옵션 | 동작 |
|------|------|
| `onboard` | 전체 온보딩 흐름 실행 |
| `create "훅"` | 슬라이드쇼 생성 + 게시 |
| `create --generate-only "훅"` | 이미지만 생성 (게시 안 함) |
| `create --tiktok-only "훅"` | TikTok만 게시 |
| `create --instagram-only "훅"` | Instagram만 게시 |
| `report` | 일일 분석 리포트 |
| `report --weekly` | 주간 리포트 |
| `research "경쟁사"` | 경쟁사 리서치 |
| `status` | 설정 상태 확인 |

## 필수 환경 변수 (~/.env)

```
# Gemini (이미지 생성)
GEMINI_API_KEY=your-gemini-api-key

# Postiz (멀티플랫폼 게시)
POSTIZ_API_KEY=your-postiz-api-key

# Cloudinary (Instagram 캐러셀용 이미지 호스팅)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

## 설정 파일

설정 파일 위치: `~/.social-slide-marketing/config.json`

온보딩 시 자동 생성된다. 수동 편집도 가능:

```bash
# 설정 초기화
python3 ~/.claude/commands/social-slide-marketing/scripts/onboarding.py --init

# 설정 검증
python3 ~/.claude/commands/social-slide-marketing/scripts/onboarding.py --validate
```

## 비용

| 항목 | 비용 |
|------|------|
| Gemini 3 Pro | ~$0.80/슬라이드쇼 (6장) |
| 하루 3개 | ~$2.40/일 |
| 월간 (90개) | ~$72/월 |
| Postiz | ~$10-30/월 |
| **총 예상** | **~$82-102/월** |

## 백업 경로

Postiz 장애 시 기존 인프라로 직접 게시:

```bash
# Instagram 직접 게시 (card-news 스킬 인프라)
python3 ~/.claude/commands/card-news/scripts/upload_cloudinary.py [이미지] --folder social-slides
python3 ~/.claude/commands/card-news/scripts/post_instagram.py --images "URL1,URL2,..." --caption "캡션"

# Threads 직접 게시
python3 ~/.claude/commands/card-news/scripts/post_threads.py --images "URL1,URL2,..." --text "텍스트"
```

## 레퍼런스

- [슬라이드 구조 공식](references/slide-structure.md)
- [분석 & 피드백 루프](references/analytics-loop.md)
- [카테고리별 템플릿](references/app-categories.md)
- [경쟁사 리서치 가이드](references/competitor-research.md)
- [플랫폼별 스펙](references/platform-specs.md)

## 제한사항

- TikTok 슬라이드쇼: 최소 2장, 최대 35장 (우리는 6장 고정)
- TikTok 초안 게시 후 사운드 추가는 수동 필수 (~60초) - `autoAddMusic: true` 설정으로 자동화 가능
- Instagram 캐러셀: 최대 10장
- Gemini 이미지: 한글 렌더링 품질 불안정 → 텍스트 오버레이로 보완
- Postiz API: 베타 기능 변경 가능
- 비용: 하루 3개 기준 ~$2.40 (Gemini API)

## 트러블슈팅

### Gemini API 에러
- `~/.env`에서 `GEMINI_API_KEY` 확인
- 할당량 초과 시 잠시 대기 후 재시도
- 이미지 생성 실패 시 프롬프트 단순화

### Postiz 게시 실패
- API Key 유효성 확인
- Integration ID 정확한지 확인
- Postiz 대시보드에서 연결 상태 확인
- 백업 경로(card-news 인프라) 사용 고려

### 텍스트 오버레이 깨짐
- Pillow 설치 확인: `pip install Pillow`
- 한글 폰트 설치 확인 (NanumGothic 또는 Pretendard)
- 시스템 폰트 경로 확인

### TikTok 조회수 낮음
- 계정 워밍업 완료 여부 확인
- 트렌딩 사운드 추가했는지 확인
- 훅 공식 재검토 (references/slide-structure.md)
- 게시 시간 최적화 (한국: 07:30, 16:30, 21:00)
