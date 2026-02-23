# 경쟁사 리서치 가이드

## 개요

경쟁사 리서치는 성공적인 슬라이드쇼 마케팅의 핵심이다.
다른 사람이 검증한 훅, 스타일, 전략을 참고하여 시행착오를 줄인다.

## 리서치 대상

### 직접 경쟁사

동일한 앱/제품을 홍보하는 계정:
- 같은 카테고리의 앱 프로모션 계정
- 해당 앱의 공식 TikTok/Instagram
- 관련 인플루언서

### 간접 경쟁사

슬라이드쇼 형태로 앱을 홍보하는 모든 계정:
- 다른 카테고리지만 같은 형태의 콘텐츠
- "앱 추천" 계정들
- AI 이미지 슬라이드쇼 계정

---

## 리서치 방법

### 방법 1: TikTok 직접 검색

```
1. TikTok 앱에서 검색:
   - "[카테고리] app" (예: "productivity app")
   - "[카테고리] 앱 추천" (예: "생산성 앱 추천")
   - "app that [benefit]"
   - "[앱이름] review"

2. 필터:
   - 최근 1개월
   - 조회수 높은 순

3. 기록할 정보:
   - 계정명 & URL
   - 훅 텍스트 (첫 장)
   - 이미지 스타일
   - 조회수
   - 캡션 스타일
```

### 방법 2: exa MCP 활용

Claude Code에서 exa MCP를 사용하여 자동 검색:

```
exa web_search_exa:
  query: "TikTok slideshow [앱 카테고리] app promotion viral"
  numResults: 10

exa company_research_exa:
  companyName: "[경쟁 앱 이름]"
```

### 방법 3: hyperbrowser MCP 활용

브라우저를 통한 심층 리서치:

```
hyperbrowser scrape_webpage:
  url: "https://www.tiktok.com/@[경쟁사계정]"

hyperbrowser search_with_bing:
  query: "[앱이름] TikTok marketing slideshow viral"
```

---

## 기록 관리

### competitor_research.py 사용

```bash
# 경쟁사 추가
python3 ~/.claude/commands/social-slide-marketing/scripts/competitor_research.py \
  --action add \
  --name "CompetitorApp" \
  --tiktok "https://tiktok.com/@competitorapp" \
  --instagram "https://instagram.com/competitorapp" \
  --notes "슬라이드쇼 스타일: 미니멀, 블루톤. 매일 2-3개 게시."

# 경쟁사 훅 기록
python3 ~/.claude/commands/social-slide-marketing/scripts/competitor_research.py \
  --action add-hook \
  --name "CompetitorApp" \
  --hook "I found an app that saves 3 hours daily" \
  --views "150K" \
  --notes "미니멀 이미지 + 큰 텍스트. 음악: trending sound."

# 모든 경쟁사 조회
python3 ~/.claude/commands/social-slide-marketing/scripts/competitor_research.py \
  --action list

# 훅 패턴 분석
python3 ~/.claude/commands/social-slide-marketing/scripts/competitor_research.py \
  --action analyze
```

---

## 분석 체크리스트

경쟁사 슬라이드쇼를 볼 때 확인할 항목:

### 훅 (Hook)

- [ ] 훅 텍스트가 무엇인가?
- [ ] 어떤 훅 공식을 사용하는가? (Discovery / Command / Question)
- [ ] 훅 이미지가 어떤 스타일인가?
- [ ] 텍스트 위치는 어디인가?
- [ ] 이모지를 사용하는가?

### 이미지 (Visual)

- [ ] 이미지 스타일 (사진/일러스트/미니멀/볼드)
- [ ] 컬러 팔레트 (주 색상)
- [ ] 텍스트 폰트 및 크기
- [ ] 앱 UI 스크린샷 포함 여부
- [ ] 이미지당 텍스트 양

### 구조 (Structure)

- [ ] 총 슬라이드 수
- [ ] 각 슬라이드의 역할
- [ ] 스토리 흐름 (문제 → 해결 → CTA)
- [ ] CTA 위치 (마지막 장 / 캡션 / 양쪽)

### 캡션 (Caption)

- [ ] 캡션 길이
- [ ] 스토리텔링 여부
- [ ] CTA 유형 (바이오 링크 / 댓글 / DM)
- [ ] 해시태그 수 및 종류

### 성과 (Performance)

- [ ] 조회수
- [ ] 좋아요/댓글/공유 비율
- [ ] 댓글 내용 (긍정/부정/질문)
- [ ] 게시 시간
- [ ] 사운드 사용 여부

---

## 경쟁사 데이터 구조

`~/.social-slide-marketing/competitors.json`:

```json
{
  "competitors": [
    {
      "name": "AppName",
      "url": "https://appname.com",
      "tiktok": "https://tiktok.com/@appname",
      "instagram": "https://instagram.com/appname",
      "notes": "전반적 관찰 메모",
      "hooks": [
        {
          "text": "I found an app that...",
          "views": "150K",
          "notes": "미니멀 스타일, 트렌딩 사운드",
          "date": "2026-02-18"
        }
      ],
      "added_at": "2026-02-18T12:00:00",
      "updated_at": "2026-02-18T12:00:00"
    }
  ]
}
```

---

## 리서치 주기

| 주기 | 활동 | 도구 |
|------|------|------|
| 매일 | TikTok FYP 스크롤하며 성공 슬라이드쇼 저장 | TikTok 앱 |
| 주 1회 | 저장한 슬라이드쇼 분석 + 훅 기록 | competitor_research.py |
| 월 1회 | 전체 경쟁사 재분석 + 트렌드 업데이트 | exa + hyperbrowser |
| 분기 1회 | 카테고리 전체 리셋 + 새 경쟁사 발굴 | 전체 도구 |

---

## 벤치마크

### 초기 목표 (1-2개월차)

- 조회수: 평균 5,000+ / 슬라이드쇼
- 참여율: 2%+
- 팔로워 성장: 주 100+

### 성장 목표 (3-6개월차)

- 조회수: 평균 20,000+
- 참여율: 3%+
- 팔로워 성장: 주 500+
- 바이럴 콘텐츠: 월 1개+ (100K+ views)

### 성숙 목표 (6개월+)

- 조회수: 평균 50,000+
- 참여율: 4%+
- 팔로워: 10K+
- 전환: 바이오 클릭 1%+
