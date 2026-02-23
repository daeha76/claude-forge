# 6슬라이드 공식 + 훅 작성법

## 6슬라이드 구조

모든 슬라이드쇼는 6장으로 구성된다. 각 장은 정확한 역할이 있다.

### 슬라이드별 역할

| # | 이름 | 역할 | 텍스트 오버레이 | 시간 |
|---|------|------|----------------|------|
| 1 | **훅** | 스크롤 멈추기 | 훅 텍스트 (1줄) | 1-2초 |
| 2 | **문제** | 공감 유발 | 문제 설명 (2-3줄) | 2-3초 |
| 3 | **발견** | 솔루션 소개 | "이걸 발견했는데..." | 2-3초 |
| 4 | **변환 1** | 핵심 기능 시연 | 기능/결과 설명 | 2-3초 |
| 5 | **변환 2** | 추가 기능 시연 | 추가 결과 설명 | 2-3초 |
| 6 | **CTA** | 행동 유도 | CTA 텍스트 | 2-3초 |

### 슬라이드 1: 훅 (Hook)

**목적**: 첫 0.5초 안에 스크롤을 멈추게 한다.

**이미지 규칙**:
- 강렬한 비주얼 (대비, 색상, 감정)
- 앱 UI가 아닌 상황/감정 표현
- 텍스트 오버레이를 위한 여백 확보

**텍스트 규칙**:
- 최대 1줄 (4-6 단어)
- 이미지 상단 30% 위치 (TikTok 안전 영역)
- 큰 폰트 (이미지 너비의 6.5%)

### 슬라이드 2: 문제 (Problem)

**목적**: 타겟 오디언스의 고통을 자극한다.

**이미지 규칙**:
- 좌절/혼란/스트레스 상황
- 타겟이 일상에서 겪는 장면
- 살짝 어두운 톤 (문제 강조)

**텍스트 규칙**:
- 2-3줄 (문제 설명)
- "~해서 힘들었던 적 있으시죠?"
- 질문형이 효과적

### 슬라이드 3: 발견 (Discovery)

**목적**: 해결책의 존재를 알린다.

**이미지 규칙**:
- 밝아지는 톤 (전환점)
- 스마트폰/노트북에서 뭔가 발견하는 장면
- 놀람/기쁨 표정

**텍스트 규칙**:
- "이걸 발견했는데..." / "그런데 이 앱을 알게 됐어요"
- 호기심 유발
- 앱 이름 첫 등장

### 슬라이드 4: 변환 1 (Transformation 1)

**목적**: 핵심 기능/결과를 보여준다.

**이미지 규칙**:
- 밝고 긍정적인 톤
- 앱 사용 중인 모습 (UI 스크린샷 느낌)
- Before→After가 명확한 비주얼

**텍스트 규칙**:
- 핵심 기능 1가지
- 구체적 수치/결과 포함 ("3일 만에 ~")
- 간결하게

### 슬라이드 5: 변환 2 (Transformation 2)

**목적**: 추가 가치를 보여준다.

**이미지 규칙**:
- 확장된 사용 시나리오
- 여러 기능 또는 결과물
- 더 밝고 풍부한 비주얼

**텍스트 규칙**:
- 추가 기능 2-3개 나열
- "게다가 ~도 할 수 있어요"
- 가치 스택킹

### 슬라이드 6: CTA (Call to Action)

**목적**: 즉시 행동하게 만든다.

**이미지 규칙**:
- 깨끗한 배경 (텍스트 가독성)
- 긍정적/성취감 느낌
- 로고나 앱 아이콘 포함 가능

**텍스트 규칙**:
- 명확한 CTA 1개
- "바이오 링크에서 무료로 시작하세요"
- 긴급성 또는 희소성 추가 가능

**참여 유도형 CTA (Engagement Farming)**:
- "댓글에 손 남기면 링크 보내드림" (DM 유도 + 댓글 수 증가)
- "이거 필요한 사람?" (질문형 참여 유도)
- "저장해두세요 나중에 찾기 힘듦" (Instagram 저장 유도)
- "궁금한 거 있으면 댓글 남겨" (댓글 유도)
- "친구 태그해 같이 써봐" (공유 유도)

---

## 아키텍처 락킹 (Scene Locking)

6장 슬라이드 전체가 **하나의 장면 설명(scene description)**을 공유해야 한다. 인물(person), 환경(environment), 카메라 앵글(camera), 아트 스타일(art style)은 모든 슬라이드에서 동일하며, 슬라이드별로 감정(emotion), 분위기(mood), 색조(color grading)만 변경한다.

### 왜 필요한가

- 각 슬라이드마다 다른 인물/배경이 나오면 "AI 짜집기" 느낌이 난다
- 시각적 일관성이 있어야 스토리텔링이 성립한다
- 동일 장면에서 감정/색조 변화만으로 충분한 시각적 대비를 만들 수 있다

### 장면 설정 방법

- **자동 생성**: config의 `category`에 따라 카테고리별 기본 장면이 자동 생성됨
- **수동 설정**: config의 `sceneDescription` 필드에 직접 장면을 지정

### 예시

```
scene_lock = "28세 한국 여성, 어깨까지 오는 검은 머리, 흰 티셔츠,
나무 책상 앞 모던 아파트, 큰 창문으로 오후 자연광,
디지털 일러스트레이션 스타일, 아이레벨 미디엄 샷"

slide_1 = f"{scene_lock}. 스트레스 받은 표정, 서류 흩어짐, 탁한 색조."
slide_3 = f"{scene_lock}. 폰을 보며 놀란 표정, 밝은 색조가 나타남."
slide_6 = f"{scene_lock}. 자신감 있는 미소, 정리된 책상, 생동감 있는 색조."
```

### 락킹되는 요소 vs 변하는 요소

| 락킹 (6장 동일) | 변동 (슬라이드별) |
|-----------------|-------------------|
| 인물 외모/의상 | 표정/감정 |
| 환경/배경 | 조명 톤/색조 |
| 카메라 앵글 | 소품 배치 |
| 아트 스타일 | 분위기/무드 |

---

## 검증된 훅 공식

### Tier 1: 최고 성과 (검증됨)

| 공식 | 예시 (영문) | 예시 (한국어 일기체) |
|------|------------|---------------------|
| I found an app that [benefit] | I found an app that writes emails for you | 이메일 대신 써주는 앱 찾음 ㄹㅇ 대박 |
| Stop [behavior], use [app] instead | Stop using ChatGPT for images, use this instead | ChatGPT로 이미지 만들지 마 이거 써봐 |
| This app will [transform] in [time] | This app will double your productivity in 1 week | 이거 1주일 써봤는데 생산성 2배 됨 ㅋㅋ |
| [앱] 써봤는데 진짜 [결과] | - | 이 앱 써봤는데 진짜 인생 바뀜 |
| [문제] 때문에 고민이면 이거 | - | 영어 공부 고민이면 이거 써봐 |

### Tier 2: 좋은 성과

| 공식 | 예시 |
|------|------|
| I've been using [app] for [time] and [result] | I've been using Notion for 6 months and... |
| Why does nobody talk about [app]? | Why does nobody talk about this free AI tool? |
| [Number]% of people don't know about [app] | 90% of people don't know this app exists |
| 이거 진짜 숨겨진 앱인데... | 이거 진짜 숨겨진 앱인데 아는 사람 없음 |
| [직업/상황]이면 이 앱 필수임 | 프리랜서면 이 앱 필수임 ㄹㅇ |

### Tier 3: 보통 성과 (차별화 필요)

| 공식 | 예시 |
|------|------|
| The [category] app that changed my [area] | The productivity app that changed my mornings |
| [App] vs [competitor] | Notion vs ClickUp - here's why I switched |
| My [time] results using [app] | My 30-day results using this fitness app |
| [경쟁앱] 쓰다가 [앱]으로 갈아탐 | 노션 쓰다가 이걸로 갈아탐 이유 있음 |

---

## 훅 작성 규칙

### 필수 규칙

1. **4-8 단어**: 짧을수록 좋다
2. **구체적**: "좋은 앱" (X) → "이메일을 대신 써주는 앱" (O)
3. **감정 유발**: 호기심, 놀라움, FOMO
4. **클릭베이트 금지**: 과장은 OK, 거짓은 NO
5. **첫 단어가 핵심**: "I found", "Stop", "This app", "이거"

### 한국어 훅 특수 규칙

1. **일기체(반말) 기본**: TikTok 훅은 일기체가 기본이다. "~해봄", "~임", "~됨", "ㄹㅇ", "ㅋㅋ" 사용. "~해보세요", "~합니다", "~하는 방법" 같은 존댓말/설명체는 사용하지 않는다.
2. **이모지 1개**: 훅 앞에 이모지 하나 추가 가능
3. **숫자 포함**: "3가지 이유" 같은 숫자가 클릭률 높임
4. **질문형**: "~해봄?" / "~인 사람?" 형태가 효과적 (존칭 질문 X)
5. **트렌드어**: 그때그때 유행하는 표현 활용
6. **금지 패턴**: "~하는 방법", "~하세요", "~입니다", "꼭 ~해보세요" (광고처럼 보임)

### A/B 테스트 전략

같은 콘텐츠를 다른 훅으로 2개 만들어 비교:

1. 첫 주: 매일 2개씩 게시 (훅만 다르게)
2. 3일 후 조회수 비교
3. 높은 조회수 훅 공식을 더 많이 사용
4. 낮은 조회수 훅 공식은 폐기 또는 수정

---

## 이미지 프롬프트 가이드 (Gemini 3 Pro)

### 기본 프롬프트 구조

```
[스타일 지시어], [비율 지시어], [장면 설명], [분위기], [제외 사항]
```

### 스타일 옵션

| 스타일 | 프롬프트 키워드 | 적합한 카테고리 |
|--------|---------------|---------------|
| 미니멀 | "Minimalist, clean, flat design" | SaaS, 생산성, 교육 |
| 볼드 | "Bold, vibrant, high contrast" | 피트니스, 뷰티, F&B |
| 일러스트 | "Digital illustration, friendly" | 교육, 키즈, 라이프스타일 |
| 사진풍 | "Photorealistic, cinematic" | 여행, 음식, 패션 |
| 네온 | "Neon, dark background, glowing" | 게임, 테크, 나이트라이프 |

### 필수 포함 지시어

```
- "No text on the image" (텍스트 오버레이를 별도로 하므로)
- "Vertical 9:16 format"
- "High quality, suitable for social media"
- "Leave space at top 30% for text overlay"
```

### 프롬프트 예시

**생산성 앱:**
```
Modern, clean digital illustration. Vertical 9:16 format.
A person looking at their phone screen with amazement, discovering
a new productivity tool. Bright, optimistic office background.
No text on the image. Leave space at top for text overlay.
```

**피트니스 앱:**
```
Bold, vibrant photography style. Vertical 9:16 format.
Athletic person using a fitness tracking app on their phone,
showing workout progress. Energetic gym setting with dramatic lighting.
No text on the image. High quality social media content.
```

---

## 캡션 템플릿

### 스토리텔링 캡션 (가장 효과적)

```
[훅 반복 (1줄)]

[개인 스토리 (2-3줄)]
- 어떤 문제가 있었고
- 이걸 발견해서
- 이런 결과를 얻었다

[CTA (1줄)]
바이오 링크에서 시작하세요

[해시태그 (3-5개)]
#앱추천 #생산성앱 #꿀팁
```

### 정보 제공형 캡션

```
[앱 이름]이 대단한 3가지 이유:

1. [기능/혜택 1]
2. [기능/혜택 2]
3. [기능/혜택 3]

무료로 시작해보세요 (바이오 링크)

#앱추천 #무료앱 #생산성
```

### 질문형 캡션

```
[질문으로 시작]
혹시 [문제]로 고민해본 적 있으세요?

저도 그랬는데, [앱]을 쓰고 나서
[결과]가 완전히 달라졌어요.

어떻게? 댓글에 "방법" 남겨주세요!

#꿀팁 #앱추천
```

---

## 텍스트 오버레이 규칙 (CRITICAL)

### 폰트 크기

- **기본**: 이미지 너비의 6.5% (1080px 이미지 → 70px 폰트)
- **강조**: 최대 8% (짧은 텍스트에만)
- **보조**: 최소 4% (부가 설명)

### 위치 (안전 영역)

TikTok/Instagram 인터페이스 요소를 피해야 한다:

```
┌──────────────────┐
│  TikTok 상단 UI   │ ← 상위 10% 금지
│                   │
│  ■ 텍스트 위치 ■  │ ← 20-40% 영역 (안전)
│                   │
│                   │
│                   │ ← 중앙은 이미지 영역
│                   │
│  좋아요/댓글 버튼  │ ← 우측 하단 금지
│  캡션 영역        │ ← 하위 25% 금지
└──────────────────┘
```

### 가독성

1. **흰색 텍스트 + 검정 아웃라인** (기본)
2. **반투명 배경 박스** (복잡한 배경일 때)
3. **그림자**: 2px offset, 50% opacity 검정
4. **줄 간격**: 폰트 크기의 130%

### 한글 특수 규칙

- **줄 간격 확대**: line-height 1.7 이상 (한글 가독성)
- **글자당 너비**: 한글은 영문 대비 1.5배 넓으므로 4자/줄 기준
- **폰트**: Pretendard Bold > NanumGothic Bold > NotoSansKR Bold
