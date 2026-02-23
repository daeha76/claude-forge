# Postiz API + 피드백 루프 문서

## Postiz API 레퍼런스

### Base URL

```
https://api.postiz.com/public/v1
```

### 인증

```
Authorization: {POSTIZ_API_KEY}
Content-Type: application/json
```

> **참고**: Postiz API는 Bearer prefix 없이 raw API key를 직접 전달합니다.

### 핵심 엔드포인트

#### 포스트 생성

```
POST /posts
```

```json
{
  "type": "now",
  "posts": [
    {
      "integration": {"id": "integration-id"},
      "value": [{"content": "캡션", "image": ["media-refs"]}],
      "settings": {
        "__type": "tiktok",
        "title": "제목",
        "privacy_level": "SELF_ONLY",
        "video_made_with_ai": true,
        "content_posting_method": "DIRECT_POST",
        "duet": false,
        "stitch": false,
        "comment": true,
        "autoAddMusic": true,
        "brand_content_toggle": false,
        "brand_organic_toggle": false
      }
    }
  ]
}
```

**type 옵션:**
- `"now"`: 즉시 게시
- `"schedule"`: 예약 게시 (date 필드 필요)
- `"draft"`: 초안 저장

**privacy_level (TikTok):**
- `"SELF_ONLY"`: 본인만 보기 (초안용, 트렌딩 사운드 추가 후 공개)
- `"MUTUAL_FOLLOW_FRIENDS"`: 맞팔만
- `"FOLLOWER_OF_CREATOR"`: 팔로워만
- `"PUBLIC_TO_EVERYONE"`: 모든 사람

#### 포스트 목록 조회

```
GET /posts
```

응답:
```json
{
  "data": [
    {
      "id": "post-id",
      "content": "캡션 텍스트",
      "createdAt": "2026-02-18T12:00:00Z",
      "integrations": [
        {
          "type": "tiktok",
          "externalId": "tiktok-video-id"
        }
      ]
    }
  ]
}
```

#### 포스트 분석

```
GET /posts/{post-id}/analytics
```

응답:
```json
{
  "analytics": {
    "views": 12500,
    "likes": 450,
    "comments": 32,
    "shares": 89,
    "impressions": 15000,
    "reach": 11000
  }
}
```

#### 미디어 업로드

```
POST /upload
Content-Type: multipart/form-data

file: [binary]
```

응답:
```json
{
  "id": "media-id",
  "url": "https://..."
}
```

#### Integration 목록

```
GET /integrations
```

응답:
```json
{
  "data": [
    {
      "id": "integration-id",
      "type": "tiktok",
      "name": "My TikTok Account"
    }
  ]
}
```

---

## 피드백 루프 시스템

### 일일 루프 (Daily Loop)

```
매일 오전 9시 (KST):
1. Postiz API에서 최근 3일 포스트 조회
2. 각 포스트의 분석 데이터 수집
3. 진단 프레임워크 적용
4. 훅 성과 파일 업데이트
5. 리포트 생성
```

### 주간 루프 (Weekly Loop)

```
매주 월요일 오전 9시 (KST):
1. 최근 7일 전체 분석
2. 훅 성과 트렌드 분석
3. CTA 효과 비교
4. 다음 주 콘텐츠 전략 추천
5. 주간 리포트 생성
```

---

## 진단 프레임워크

### 6분면 매트릭스

```
                    전환율 높음
                        │
    FIX HOOKS           │  BOOST        │  SCALE IT
    (낮은 조회수,       │  (중간 조회수, │  (높은 조회수,
     높은 전환)         │   높은 전환)   │   높은 전환)
                        │               │
  ──────────────────────┼───────────────┼──── 조회수
         <10K           │   10K-50K     │   50K+
                        │               │
    FULL RESET          │  OPTIMIZE     │  FIX CTA
    (낮은 조회수,       │  (중간 조회수, │  (높은 조회수,
     낮은 전환)         │   낮은 전환)   │   낮은 전환)
                        │               │
                    전환율 낮음
```

### 진단별 조치

#### SCALE IT (높은 조회수 + 높은 전환)

```
즉시 조치:
1. 동일 훅 공식으로 변형 3개 제작
2. 다른 시간대에 게시하여 도달 극대화
3. 해당 훅을 '골든 훅'으로 저장
4. 유사 앵글로 5-10개 추가 콘텐츠 계획

장기 조치:
1. 유료 프로모션 투입 고려 (TikTok Promote)
2. 해당 컨셉으로 시리즈 제작
3. 다른 플랫폼에도 동일 전략 적용
```

#### FIX CTA (높은 조회수 + 낮은 전환)

```
즉시 조치:
1. CTA 슬라이드 교체 (더 직접적으로)
2. 캡션의 CTA 변경
3. 바이오 링크 최적화 (랜딩 페이지 A/B 테스트)
4. "댓글에 OOO 남기세요" 형태로 CTA 변경

장기 조치:
1. CTA 위치 실험 (슬라이드 5에 CTA 추가)
2. 프로모 코드/할인 CTA 테스트
3. DM 자동응답 봇 설정 (ManyChat 등)
```

#### BOOST (중간 조회수 + 높은 전환)

```
즉시 조치:
1. 유료 프로모션 집행 (TikTok Promote)
2. 리포스트/듀엣 유도 캠페인
3. 게시 시간 최적화 (피크 타임 재테스트)
4. 해시태그 확장 (관련 니치 태그 추가)

장기 조치:
1. 동일 훅 공식으로 변형 제작
2. 크로스 플랫폼 동시 게시 강화
3. 콜라보/멘션 전략으로 도달 확대
```

#### OPTIMIZE (중간 조회수 + 낮은 전환)

```
즉시 조치:
1. 훅/CTA 미세 조정 (A/B 테스트)
2. 캡션 CTA 강화
3. 슬라이드 구성 재배열
4. 타겟 해시태그 최적화

장기 조치:
1. 전환 퍼널 점검 (바이오 링크 → 랜딩)
2. CTA 위치/문구 실험
3. 경쟁사 성공 패턴 벤치마킹
```

#### FIX HOOKS (낮은 조회수 + 높은 전환)

```
즉시 조치:
1. 훅 교체 (Tier 1 공식 사용)
2. 첫 장 이미지 더 자극적으로 변경
3. 게시 시간 변경 (피크 타임)
4. 해시태그 최적화

장기 조치:
1. A/B 테스트 강화 (매일 2개씩 훅 비교)
2. 경쟁사 성공 훅 분석 강화
3. 트렌드 사운드 적극 활용
```

#### FULL RESET (낮은 조회수 + 낮은 전환)

```
즉시 조치:
1. 경쟁사 재분석 (최근 1주 성공 콘텐츠)
2. 완전히 새로운 앵글 시도
3. 타겟 오디언스 재정의
4. 이미지 스타일 변경

장기 조치:
1. 제품/앱의 USP 재검토
2. 다른 카테고리 프롬프트 시도
3. 다른 플랫폼 우선 공략 고려
4. 계정 건강 상태 점검
```

---

## 3-Layer 퍼널 진단

### 퍼널 구조

Views → Link Clicks → Conversions

| 레이어 | 소스 | 건강한 수준 |
|--------|------|------------|
| Views | Postiz API | 10K+ per post |
| Link Clicks | Bitly/UTM | 조회수의 1-3% |
| Conversions | 수동/RevenueCat | 클릭의 5-15% |

### 병목 진단

| 시나리오 | 진단 | 조치 |
|---------|------|------|
| 높은 조회수 + 낮은 클릭 | CTA 약함 | CTA 슬라이드/캡션 개선 |
| 높은 클릭 + 낮은 전환 | 랜딩/앱 문제 | 랜딩 페이지 최적화 |
| 낮은 조회수 | 도달 부족 | 훅 교체, 시간 최적화 |
| 전체 양호 | 건강한 퍼널 | 볼륨 확대 |

---

## 훅 공식 자동 랭킹

### 개요

훅 텍스트에서 공식 패턴(예: "I found an app that", "Stop ~, use ~ instead")을 자동 감지하고, 성과 데이터 기반으로 공식별 랭킹을 계산한다.

### 랭킹 계산 방식

- 각 공식 패턴별 평균 조회수를 계산
- 전체 평균 조회수(global avg)와 비교하여 등급 부여

### 자동 승급/강등 규칙

| 조건 | 결과 |
|------|------|
| 평균 조회수 > global avg AND count >= 3 | tier1으로 승급 |
| 평균 조회수 < global avg * 0.5 AND count >= 5 | tier3로 강등 |
| 그 외 | 현재 등급 유지 |

### 저장 위치

`~/.social-slide-marketing/hook-rankings.json`

```json
{
  "rankings": {
    "discovery": { "tier": 1, "avg_views": 52000, "count": 8 },
    "stop_using": { "tier": 1, "avg_views": 48000, "count": 5 },
    "percentage": { "tier": 3, "avg_views": 8000, "count": 6 }
  },
  "global_avg_views": 35000,
  "last_updated": "2026-02-18T09:00:00Z"
}
```

### 활용

- `create` 워크플로우 Step 1에서 tier1 공식 위주로 훅 추천
- `report`에서 공식별 성과 트렌드 표시
- 강등된 공식은 경고 표시

---

## 학습 시스템

### 개요

실패/성공 패턴을 자동으로 기록하여 향후 콘텐츠 제작에 반영한다.

### 추적 패턴

| 패턴 | 비교 | 저장 키 |
|------|------|---------|
| 훅 길이 | 짧은 훅 (4-6단어) vs 긴 훅 (7-10단어) 평균 조회수 | `hook_length` |
| 언어 | 한국어 vs 영어 훅 평균 조회수 | `language` |
| 문장 유형 | 질문형 vs 서술형 평균 조회수 | `sentence_type` |
| 게시 시간 | 시간대별 평균 조회수 | `posting_time` |
| CTA 유형 | CTA 유형별 전환율 | `cta_type` |

### 저장 위치

`~/.social-slide-marketing/learnings.json`

```json
{
  "learnings": [
    {
      "pattern": "hook_length",
      "finding": "4-6 단어 훅이 7+ 단어보다 평균 2.3배 높은 조회수",
      "sample_size": 24,
      "confidence": "high",
      "date": "2026-02-18"
    },
    {
      "pattern": "posting_time",
      "finding": "21:00 KST 게시가 07:30보다 1.5배 높은 참여율",
      "sample_size": 30,
      "confidence": "high",
      "date": "2026-02-15"
    }
  ],
  "last_analysis": "2026-02-18T09:00:00Z"
}
```

### 활용

- `create` 워크플로우에서 학습 패턴 기반 추천
- `report`에서 새로운 학습 사항 표시
- 충분한 데이터 축적 시 자동으로 전략 조정

---

## 성과 임계값

### 조회수 기준 (TikTok)

| 등급 | 조회수 | 판단 |
|------|--------|------|
| 대박 | 100K+ | 즉시 SCALE |
| 성공 | 50K+ | SCALE or FIX CTA |
| 보통 | 10K-50K | 최적화 필요 |
| 부진 | <10K | 훅 또는 전체 리셋 |

### 참여율 기준

| 등급 | 참여율 | 계산 |
|------|--------|------|
| 우수 | 5%+ | (좋아요+댓글+공유) / 조회수 |
| 양호 | 3-5% | 평균 이상 |
| 보통 | 1-3% | 평균 |
| 부진 | <1% | CTA/콘텐츠 문제 |

### 전환 기준

전환은 제품/서비스에 따라 다르지만 일반적:

| 방법 | 추적 | 좋은 수준 |
|------|------|----------|
| 바이오 링크 클릭 | Bitly/Linktree 통계 | 조회수의 1-3% |
| 앱 다운로드 | 앱스토어 통계 | 바이오 클릭의 10-30% |
| 회원가입 | UTM + GA4 | 바이오 클릭의 5-15% |
| DM 수 | 수동 카운트 | 조회수의 0.1-0.5% |

---

## 훅 성과 추적 (hook-performance.json)

### 데이터 구조

```json
{
  "performances": [
    {
      "post_id": "abc123",
      "hook": "I found an app that...",
      "date": "2026-02-18T12:00:00Z",
      "views": 45000,
      "likes": 1200,
      "comments": 89,
      "shares": 234,
      "engagement_rate": 3.38,
      "diagnosis": "FIX CTA",
      "hook_formula": "tier1_discovery"
    }
  ]
}
```

### 자동 분석

weekly report에서 자동으로:
1. 훅 공식별 평균 조회수 계산
2. 최고/최저 성과 훅 식별
3. 시간대별 성과 비교
4. CTA 유형별 전환율 비교
5. 다음 주 전략 추천 생성

---

## 크론 설정

### macOS crontab

```bash
# 매일 오전 9시 일일 리포트
0 9 * * * /usr/bin/python3 ~/.claude/commands/social-slide-marketing/scripts/daily_report.py

# 매주 월요일 오전 9시 주간 리포트
0 9 * * 1 /usr/bin/python3 ~/.claude/commands/social-slide-marketing/scripts/daily_report.py --weekly

# 매일 오후 6시 분석 데이터 수집 + 성과 업데이트
0 18 * * * /usr/bin/python3 ~/.claude/commands/social-slide-marketing/scripts/check_analytics.py --update-performance
```

### n8n 워크플로우 (대안)

n8n MCP를 통해 워크플로우 자동화 가능:
1. Schedule Trigger → 매일 9AM KST
2. Execute Command → daily_report.py
3. Gmail → 리포트 이메일 발송
4. Slack/Discord → 팀 채널 알림
