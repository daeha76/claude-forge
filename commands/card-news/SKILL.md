---
name: card-news
description: 카드뉴스 생성 → 이미지 호스팅 → Instagram + Threads 자동 포스팅
---

# Card News Pipeline

카드뉴스를 생성하고 Instagram + Threads에 자동 포스팅하는 파이프라인.

## 사용법

```bash
# 기본: 카드뉴스 생성 + 인스타 + 스레드 포스팅
/card-news 주제: AI 자동화 트렌드

# 이미지만 생성 (포스팅 안 함)
/card-news --generate-only 주제: 2026 마케팅 전략

# 인스타만 포스팅
/card-news --instagram-only 주제: SaaS 비즈니스 팁

# 스레드만 포스팅
/card-news --threads-only 주제: 개발자 생산성

# 토큰 갱신
/card-news refresh-token

# 토큰 상태 확인
/card-news check-token
```

## 실행 흐름

사용자가 `/card-news 주제: [주제]`를 실행하면:

### Step 1: 콘텐츠 기획

주제를 기반으로 카드뉴스 콘텐츠를 기획한다:
- **장수**: 3~5장 (기본 4장)
- **구성**: 각 장별 제목 + 핵심 메시지 + 시각적 설명
- **톤**: 전문적이면서 읽기 쉬운 인포그래픽 스타일
- **비율**: 4:5 (Instagram 최적 비율)

### Step 2: 이미지 생성

`generate-image` 스킬로 각 장의 이미지를 생성한다:

```bash
python3 ~/.claude/commands/generate-image/scripts/generate_image.py \
  "[각 장의 상세 프롬프트]" \
  -o /tmp/card-news/slide_01.jpg \
  -a 4:5
```

**프롬프트 작성 가이드:**
- 카드뉴스 스타일: 깔끔한 배경 + 큰 텍스트 + 아이콘/일러스트
- 일관된 컬러 팔레트 유지 (장 간 통일감)
- 텍스트는 최소화 (핵심 키워드만)
- 각 장에 번호 표시 (1/4, 2/4 등)

### Step 3: 이미지 업로드 (Cloudinary)

생성된 이미지를 Cloudinary에 업로드하여 공개 URL을 획득한다:

```bash
python3 ~/.claude/commands/card-news/scripts/upload_cloudinary.py \
  /tmp/card-news/slide_01.jpg \
  --folder card-news
```

- Instagram Graph API는 공개 HTTPS URL이 필수
- 각 이미지의 URL을 수집하여 다음 단계에 전달

### Step 4: Instagram 포스팅

캐러셀(다중 이미지) 형태로 Instagram에 포스팅한다:

```bash
python3 ~/.claude/commands/card-news/scripts/post_instagram.py \
  --images "URL1,URL2,URL3,URL4" \
  --caption "캡션 텍스트

#해시태그1 #해시태그2"
```

- 2장 이상: 캐러셀 자동 적용
- 1장: 단일 이미지 포스팅
- 캡션에 해시태그 포함 (최대 30개)

### Step 5: Threads 포스팅

동일한 콘텐츠를 Threads에 포스팅한다:

```bash
python3 ~/.claude/commands/card-news/scripts/post_threads.py \
  --images "URL1,URL2,URL3,URL4" \
  --text "포스트 텍스트"
```

- 캐러셀 또는 단일 이미지 자동 판단
- Threads 텍스트 제한: 500자

### Step 6: 결과 출력

포스팅 완료 후 결과를 요약한다:
- 생성된 이미지 수
- Instagram 포스팅 ID / URL
- Threads 포스팅 ID / URL

## 옵션 처리

| 옵션 | 동작 |
|------|------|
| (없음) | 전체 파이프라인 실행 (생성 + 업로드 + 인스타 + 스레드) |
| `--generate-only` | Step 1~2만 실행 (이미지만 생성, 로컬 저장) |
| `--instagram-only` | Step 1~4만 실행 (인스타만 포스팅) |
| `--threads-only` | Step 1~3 + Step 5만 실행 (스레드만 포스팅) |
| `refresh-token` | Instagram + Threads 토큰 갱신 |
| `check-token` | 토큰 유효성 확인 |

## 토큰 관리

### 토큰 갱신 (60일마다)
```bash
python3 ~/.claude/commands/card-news/scripts/refresh_token.py both
```

### 토큰 상태 확인
```bash
python3 ~/.claude/commands/card-news/scripts/refresh_token.py check
```

### 개별 갱신
```bash
python3 ~/.claude/commands/card-news/scripts/refresh_token.py instagram
python3 ~/.claude/commands/card-news/scripts/refresh_token.py threads
```

## 필수 환경 변수 (~/.env)

```
# Gemini (이미지 생성)
GEMINI_API_KEY=your-gemini-api-key

# Cloudinary (이미지 호스팅)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Instagram Graph API
INSTAGRAM_USER_ID=your-ig-user-id
INSTAGRAM_ACCESS_TOKEN=your-long-lived-token

# Threads API
THREADS_USER_ID=your-threads-user-id
THREADS_ACCESS_TOKEN=your-threads-token
```

## 제한사항

- Instagram: 24시간 당 25개 포스트 제한
- Instagram: 캐러셀 최대 10장
- Instagram: Stories/Reels는 API로 불가 (피드 포스트만)
- Threads: 텍스트 500자 제한
- Threads API: 베타 상태로 기능 변경 가능
- Gemini 이미지: 한글 텍스트 렌더링 품질 불안정할 수 있음
- 토큰: 60일마다 갱신 필요 (`/card-news refresh-token`)

## 트러블슈팅

### "token expired" 에러
```bash
/card-news refresh-token
```

### 이미지 업로드 실패
- `~/.env`에서 `CLOUDINARY_*` 값 확인
- Cloudinary 무료 티어 5GB 용량 확인

### Instagram 포스팅 실패
- 이미지 URL이 공개 접근 가능한지 확인 (브라우저에서 열어볼 것)
- JPEG 형식 권장
- 토큰 유효성 확인: `/card-news check-token`

### "OAuthException" 에러
- Meta Developer App에서 권한 확인
- `instagram_content_publish` 권한 필요
- `pages_read_engagement` 권한 필요
