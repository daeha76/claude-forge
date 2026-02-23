---
name: context-sync
description: |
  세션 시작 시 외부 채널(Slack, Gmail, Calendar, GitHub, Work Sessions)의 최근 활동을 병렬 수집하여 브리핑 문서를 생성하는 스킬. 놓친 맥락을 빠르게 파악할 수 있다.
  트리거: /context-sync, 컨텍스트 동기화, 브리핑, 오늘 뭐 있었어, 놓친 거 알려줘
argument-hint: '[--period 24h] [--sources all|slack,gmail,cal,gh,work]'
---

# /context-sync 스킬

## 파이프라인 개요

```
입력: /context-sync [--period 24h] [--sources all|slack,gmail,cal,gh,work]

[Phase 1] 파라미터 파싱 + 출력 디렉토리 준비

[Phase 2] 병렬 5개 subagent (Explore, sonnet)
  ├─ slack-collector    → Slack 메시지 수집
  ├─ gmail-collector    → Gmail 이메일 수집
  ├─ cal-collector      → Calendar 이벤트 수집
  ├─ gh-collector       → GitHub 알림/PR 수집
  └─ work-collector     → Work Sessions DB 조회

[Phase 3] 결과 병합 + 브리핑 문서 생성

[Phase 4] 출력 + 액션 아이템 표시
```

## 파라미터 파싱

| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| --period | 24h | 수집 기간. 예: 1h, 12h, 24h, 48h, 7d |
| --sources | all | 수집 소스. 쉼표 구분: slack,gmail,cal,gh,work |

기간 파싱 규칙:
- `Nh` → N시간 전부터 현재까지
- `Nd` → N일 전부터 현재까지
- 숫자만 입력 시 시간(h)으로 간주

예시:
```
/context-sync                          # 기본: 24시간, 모든 소스
/context-sync --period 1h              # 최근 1시간
/context-sync --sources slack,gmail    # Slack과 Gmail만
/context-sync --period 48h --sources gh,work  # 48시간, GitHub+Work만
```

## Phase 1: 준비

```bash
# 출력 디렉토리 생성
mkdir -p /tmp/context-sync/sources

# 현재 시간 및 기간 시작 시간 계산
NOW=$(date '+%Y-%m-%dT%H:%M:%S')
# period 파싱 후 START_TIME 계산
```

## Phase 2: 병렬 소스 수집

`--sources`로 지정된 소스만 활성화한다. 각 subagent 프롬프트는 `references/`에 위치.

| Subagent | MCP 도구 | 프롬프트 파일 | 출력 파일 |
|----------|---------|-------------|----------|
| slack-collector | slack 스킬의 readMessages 패턴 | `references/prompt-slack.md` | `/tmp/context-sync/sources/slack.json` |
| gmail-collector | `mcp__gmail__search_emails`, `mcp__gmail__read_email` | `references/prompt-gmail.md` | `/tmp/context-sync/sources/gmail.json` |
| cal-collector | `mcp__google-calendar__list-events` | `references/prompt-calendar.md` | `/tmp/context-sync/sources/calendar.json` |
| gh-collector | `gh api notifications`, `gh pr list` | `references/prompt-github.md` | `/tmp/context-sync/sources/github.json` |
| work-collector | `mcp__supabase__execute_sql` | `references/prompt-work.md` | `/tmp/context-sync/sources/work.json` |

### Subagent 실행 패턴

```
# --sources 파싱
active_sources = parse_sources(args.sources)  # ["slack","gmail","cal","gh","work"]

# 병렬 Task 호출
for source in active_sources:
  Task(
    subagent_type="Explore",
    prompt=Read(f"references/prompt-{source_map[source]}.md")
      + f"\n\nPERIOD: {period}\nSTART_TIME: {start_time}\nNOW: {now}"
  )
```

### 소스별 출력 JSON 스키마

```json
{
  "source": "slack|gmail|calendar|github|work",
  "period": "24h",
  "collected_at": "2026-02-22T10:00:00",
  "summary": "소스별 1-2줄 요약",
  "items": [
    {
      "timestamp": "2026-02-22T09:30:00",
      "title": "항목 제목",
      "content": "핵심 내용 요약 (3줄 이내)",
      "priority": "high|medium|low",
      "action_required": true,
      "action_description": "필요한 조치 (있으면)",
      "url": "원본 링크 (있으면)"
    }
  ],
  "stats": {
    "total_count": 10,
    "high_priority": 2,
    "action_required": 3
  }
}
```

## Phase 3: 병합 + 브리핑 생성

모든 소스 결과를 수집하여 하나의 브리핑 문서로 병합한다.

### 병합 로직

상세 병합 규칙은 `references/merge-rules.md` 참조.

핵심 병합 단계:
1. 모든 소스의 JSON 파일을 로드
2. 하이라이트 추출 (high priority + action_required)
3. 소스별 상세 정리
4. 액션 아이템 통합 목록 생성
5. 시간순 타임라인 생성

### 브리핑 문서 구조

출력 템플릿은 `references/briefing-template.md` 참조.

```markdown
# Context Sync Briefing - {날짜}

> 수집 기간: {start_time} ~ {now}
> 소스: {active_sources}
> 생성: {now}

## 하이라이트

{high priority 항목 + action_required 항목}

## 소스별 상세

### Slack
{slack 항목들}

### Gmail
{gmail 항목들}

### Calendar
{calendar 항목들}

### GitHub
{github 항목들}

### Work Sessions
{work 항목들}

## 액션 아이템

- [ ] {action 1}
- [ ] {action 2}
...

## 타임라인

{시간순 주요 이벤트}
```

저장: `/tmp/context-sync/briefing_{날짜}.md`

## Phase 4: 출력

브리핑 문서의 핵심 내용을 터미널에 표시하고, 전체 파일 경로를 안내한다.

```
## Context Sync 완료

하이라이트 {N}건 | 액션 아이템 {M}건

### 하이라이트
{top 5 하이라이트 항목}

### 급한 액션 아이템
{action_required 항목들}

전체 브리핑: /tmp/context-sync/briefing_{날짜}.md
```

## 에러 처리

| 상황 | 대응 |
|------|------|
| MCP 도구 없음 (slack 등) | 해당 소스 건너뛰고 경고 표시 |
| 소스 인증 실패 | 해당 소스 건너뛰고 에러 메시지 포함 |
| 결과 0건 (특정 소스) | "해당 기간에 활동 없음" 표시 |
| 모든 소스 실패 | 에러 요약 출력 후 중단 |
| Supabase 연결 실패 | work-collector만 건너뛰기 |
| 기간 파싱 실패 | 기본값 24h로 폴백, 경고 |

## 관련 파일

| 파일 | 용도 |
|------|------|
| `references/prompt-slack.md` | Slack 수집 subagent 프롬프트 |
| `references/prompt-gmail.md` | Gmail 수집 subagent 프롬프트 |
| `references/prompt-calendar.md` | Calendar 수집 subagent 프롬프트 |
| `references/prompt-github.md` | GitHub 수집 subagent 프롬프트 |
| `references/prompt-work.md` | Work Sessions 수집 subagent 프롬프트 |
| `references/merge-rules.md` | 병합 로직 상세 규칙 |
| `references/briefing-template.md` | 브리핑 출력 템플릿 |
| `scripts/parse-period.sh` | 기간 파싱 유틸리티 |
