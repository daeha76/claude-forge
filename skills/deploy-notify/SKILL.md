---
name: deploy-notify
description: MCP 기반 배포 알림 - Gmail + Google Calendar + N8N 연동
version: 1.0.0
---

## Overview

배포 완료 후 이해관계자에게 자동 알림을 발송하는 스킬.
`/commit-push-pr --notify` 플래그가 이 스킬을 트리거한다.

Gmail MCP로 이메일 알림, Google Calendar MCP로 배포 기록, N8N MCP로 추가 채널 알림을 발송한다.

---

## Trigger Conditions

### 직접 호출

| 트리거 | 설명 |
|--------|------|
| `/commit-push-pr --notify` | 머지 후 자동 알림 발송 |
| `/commit-push-pr --merge --notify` | 머지 + 알림 |
| `/commit-push-pr --squash --notify` | 스쿼시 머지 + 알림 |

### 자동 호출

이 스킬은 `--notify` 플래그가 없으면 실행되지 않는다.
명시적으로 요청해야만 동작한다.

---

## MCP Dependencies

| MCP 서버 | 도구 | 용도 | 필수 |
|----------|------|------|------|
| gmail | send_email | 배포 알림 이메일 발송 | Yes |
| google-calendar | create-event | 배포 기록 캘린더 이벤트 | No |
| n8n-mcp | n8n_test_workflow | Slack/Discord 추가 알림 | No |

필수 MCP가 사용 불가하면 에러를 보고하고 스킵한다.
선택 MCP가 사용 불가하면 경고만 출력하고 계속 진행한다.

---

## Pipeline

### 1. 배포 정보 수집

`/commit-push-pr`에서 전달받는 정보:

| 항목 | 출처 |
|------|------|
| PR 번호 / 제목 | `gh pr view` |
| 커밋 해시 / 메시지 | `git log` |
| 머지 브랜치 | `git branch` |
| 변경 파일 목록 | `git diff --stat` |
| 보안 스캔 결과 | 4단계 보안 검증 |
| 주의사항 | `.claude/handoff.md` |

### 2. Gmail MCP — 배포 알림 이메일

```
ToolSearch → "select:mcp__gmail__send_email"
```

**수신자 결정:**
1. 사용자에게 수신자 이메일을 확인한다.
2. 이전에 사용한 수신자가 있으면 제안한다.
3. 수신자가 없으면 스킵하고 다음 단계로.

**이메일 내용:**

```
수신: [이해관계자 이메일]
제목: [배포 알림] [커밋 메시지 요약]

안녕하세요,

다음 변경 사항이 배포되었습니다.

## 배포 정보
- PR: #[번호] [제목]
- 브랜치: [브랜치] → [베이스]
- 머지 방식: [merge/squash/rebase]
- 배포 시간: [YYYY-MM-DD HH:MM KST]

## 변경 내용 요약
[변경 파일 수]개 파일 변경

[주요 변경 사항 3줄 이내]

## 확인 필요 사항
[handoff.md 주의사항 또는 "특별한 확인 사항 없음"]

## 보안 스캔
[Pass / Warn ([N]건) / Skipped]

감사합니다.
```

**이메일 규칙:**
- 본문은 반드시 "안녕하세요"로 시작한다 (email rules 준수).
- 변경 내용은 간결하게 요약한다 (상세는 PR 링크 참조).
- 보안 스캔 결과를 포함한다.

### 3. Google Calendar MCP — 배포 기록

```
ToolSearch → "select:mcp__google-calendar__create-event"
```

**이벤트 내용:**

```
제목: [Deploy] [커밋 메시지 요약 (50자 이내)]
시작: [현재 시간]
종료: [현재 시간 + 30분]
설명:
  PR: #[번호] [URL]
  브랜치: [브랜치] → [베이스]
  변경: [N]개 파일
  보안: [Pass/Warn/Skipped]
```

**캘린더 선택:**
1. 기본 캘린더에 생성한다.
2. "Deploy" 또는 "배포" 캘린더가 있으면 해당 캘린더 사용.

**실패 시:** 경고만 출력하고 계속 진행.

### 4. N8N MCP — 추가 채널 알림 (선택)

```
ToolSearch → "select:mcp__n8n-mcp__n8n_list_workflows"
```

**동작:**
1. n8n 워크플로우 목록에서 "deploy", "배포", "notification" 키워드를 검색한다.
2. 매칭되는 워크플로우가 있으면:
   ```
   ToolSearch → "select:mcp__n8n-mcp__n8n_test_workflow"
   ```
   워크플로우를 트리거한다 (Slack, Discord, 기타 채널 알림).
3. 매칭되는 워크플로우가 없으면 스킵한다.

**실패 시:** 경고만 출력하고 계속 진행.

---

## Output

### 성공 시

```
────────────────────────────────────
  Deploy Notification (v6)
────────────────────────────────────

  Email: [수신자] 발송 완료
  Calendar: [이벤트 제목] 생성 완료
  N8N: [워크플로우명] 트리거 완료 (또는 "스킵")

────────────────────────────────────
```

### 부분 성공 시

```
────────────────────────────────────
  Deploy Notification (v6)
────────────────────────────────────

  Email: [수신자] 발송 완료
  Calendar: 실패 — [에러 메시지]
  N8N: 스킵 (워크플로우 없음)

────────────────────────────────────
```

### MCP 사용 불가 시

```
────────────────────────────────────
  Deploy Notification (v6) — Skipped
────────────────────────────────────

  Gmail MCP 사용 불가. 알림을 발송할 수 없습니다.
  수동으로 이해관계자에게 알림하세요.

────────────────────────────────────
```

---

## Error Handling

| 상황 | 동작 |
|------|------|
| Gmail MCP 사용 불가 | 알림 전체 스킵, 경고 출력 |
| Gmail MCP 타임아웃 | 1회 재시도 후 실패 시 스킵 |
| Calendar MCP 사용 불가 | Calendar만 스킵, 나머지 계속 |
| N8N MCP 사용 불가 | N8N만 스킵, 나머지 계속 |
| 수신자 미지정 | 사용자에게 확인 요청 |

---

## Integration Points

### /commit-push-pr 커맨드

이 스킬은 `/commit-push-pr --notify` 플래그에 의해 트리거된다.
9-N단계에서 실행된다.

### Email Rules

이메일 본문은 반드시 "안녕하세요"로 시작한다.
영문 이메일을 명시적으로 요청한 경우에만 예외.

### MCP Usage Tracker

모든 MCP 호출은 `~/.claude/mcp-usage.log`에 자동 기록된다 (hooks 설정).
