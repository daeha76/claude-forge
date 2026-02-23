# 브리핑 출력 템플릿

## 파일 경로

`/tmp/context-sync/briefing_{YYYY-MM-DD}.md`

## 템플릿

```markdown
# Context Sync Briefing - {YYYY-MM-DD}

> 수집 기간: {start_time} ~ {now}
> 소스: {active_sources 쉼표 구분}
> 생성: {now}

---

## 하이라이트

{high priority + action_required 항목, 최대 10건}

| # | 소스 | 항목 | 우선순위 |
|---|------|------|---------|
| 1 | [slack] | 배포 일정 월요일로 변경 | high |
| 2 | [gh] | PR #42 리뷰 요청 | high |
| 3 | [gmail] | 제안서 수정 요청 | high |

---

## 소스별 상세

### Slack ({N}건)

{slack items 시간순}

- **HH:MM** #channel: 메시지 요약 (3줄 이내)

### Gmail ({N}건)

{gmail items 시간순}

- **HH:MM** [발신자]: 제목 — 요약

### Calendar ({N}건)

{calendar items 시간순}

- **HH:MM - HH:MM** 이벤트명 (참석자 N명)

### GitHub ({N}건)

{github items 시간순}

- **HH:MM** [repo] PR/Issue #N: 제목 — 상태

### Work Sessions ({N}건)

{work items 시간순}

- **HH:MM** 세션명 — 상태 (진행률)

---

## 액션 아이템

- [ ] {action 1} — 소스: {source}, 우선순위: {priority}
- [ ] {action 2} — 소스: {source}, 우선순위: {priority}
...

---

## 타임라인

| 시간 | 소스 | 이벤트 |
|------|------|--------|
| 07:00 | [work] | SCAW Phase 1 작업 시작 |
| 08:15 | [gmail] | 제안서 수정 요청 수신 |
| 09:00 | [gh] | PR #42 리뷰 요청 |
| 09:30 | [slack] | 배포 일정 변경 공지 |
| 10:30 | [cal] | 주간 스프린트 리뷰 |

---

## 통계

| 소스 | 총 건수 | 중요 | 액션 필요 |
|------|--------|------|----------|
| Slack | {n} | {n} | {n} |
| Gmail | {n} | {n} | {n} |
| Calendar | {n} | {n} | {n} |
| GitHub | {n} | {n} | {n} |
| Work | {n} | {n} | {n} |
| **합계** | **{N}** | **{N}** | **{N}** |
```

## 터미널 출력 (축약본)

브리핑 파일 저장 후, 터미널에는 축약본을 표시:

```
## Context Sync 완료 ({YYYY-MM-DD})

하이라이트 {N}건 | 액션 아이템 {M}건

### 하이라이트 (상위 5건)
1. [slack] 배포 일정 월요일로 변경
2. [gh] PR #42 리뷰 요청
3. [gmail] 제안서 수정 요청

### 급한 액션 아이템
- [ ] PR #42 코드 리뷰 수행 (gh)
- [ ] 제안서 가격표 수정 후 회신 (gmail)

전체 브리핑: /tmp/context-sync/briefing_{날짜}.md
```
