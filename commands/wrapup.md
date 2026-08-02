---
allowed-tools: Bash(git:*), Bash(gh:*), Bash(npm:*), Bash(dotnet:*), Bash(python:*), Read, Grep, Glob, Edit, Write, Task, Skill(refactor-clean), Skill(code-review), Skill(handoff-verify), Skill(sync-docs), Skill(commit-push-pr), Skill(next-task)
description: 작업 마무리 파이프라인 — 리팩토링→리뷰→검증→문서동기화 (기본 검토만, --merge 시 출하까지)
argument-hint: "[커밋 메시지] [--merge|--squash|--rebase] [--skip-refactor] [--skip-review] [--skip-verify] [--skip-docs] [--notify] [--next-prompt]"
---

# /wrapup — 작업 마무리 파이프라인

방금 작성한 코드를 한 번에 마무리한다: **리팩토링 → 코드리뷰 → 핸드오프 검증 → 문서 동기화**.
기본은 **검토만** 하고 멈춘다. `--merge`(또는 `--squash`/`--rebase`)를 붙이면 **커밋·푸시·머지까지** 이어서 출하한다.

> `/ship`과의 차이: `/wrapup`은 **문서 동기화(sync-docs)를 포함**하고, **기본값이 머지 안 함**이다.
> 머지 옵션을 명시해야만 `/commit-push-pr`로 넘어간다. 검토만 빠르게 돌리고 싶을 때 `/wrapup`을 쓴다.

## 0단계: 인자 파싱

`$ARGUMENTS`에서 옵션 추출:

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--merge` / `--squash` / `--rebase` | (없음) | PR 머지 모드. **하나라도 있으면 6단계(출하) 실행** |
| `--skip-refactor` | false | refactor-clean 단계 스킵 |
| `--skip-review` | false | code-review 단계 스킵 |
| `--skip-verify` | false | handoff-verify 단계 스킵 |
| `--skip-docs` | false | sync-docs 단계 스킵 |
| `--notify` | false | 머지 후 MCP 알림 (출하 시에만 의미 있음) |
| `--next-prompt` | false | 머지 후 **다음 세션 시작 프롬프트** 생성 (7단계 — 출하 시에만 의미 있음) |
| 나머지 텍스트 | (자동 생성) | 커밋 메시지 (출하 시에만 사용) |

**핵심 분기**: `--merge`/`--squash`/`--rebase` 중 하나라도 있으면 `MERGE=true`. 없으면 검토 4단계만 돌고 종료.

## 1단계: 사전 체크

```bash
git status --short
git diff --name-only HEAD
git branch --show-current
```

- 변경사항 없으면 → "변경사항이 없습니다" 출력 후 중단
- 변경된 파일 목록과 개수 출력

## 2단계: Refactor (리팩토링·정리)

> `--skip-refactor` 시 스킵

방금 작성한 코드를 정리한다:
- 중복 코드 → 공통 모듈 추출
- 불필요한 복잡성·죽은 코드 제거
- 변경 전후 테스트로 안전성 검증 (테스트 깨지면 롤백)
- **코드를 직접 수정함**

실행: `/refactor-clean` 스킬 호출 (없으면 `/simplify`로 대체).
수정이 발생하면 사용자에게 변경 요약 출력.

## 3단계: Code Review (보안 + 품질 정적 검토)

> `--skip-review` 시 스킵

실행: `/code-review` 스킬 호출.

- **CRITICAL** (하드코딩 시크릿, SQL injection, XSS): 자동 수정 시도 → 재검토 → 실패 시 **파이프라인 중단**
- **HIGH** (50줄+ 함수, 누락된 에러 핸들링): 경고 후 수정 여부 확인
- **MEDIUM/LOW**: 보고만, 진행 계속

## 4단계: Handoff Verify (빌드·테스트·타입체크 자동 검증)

> `--skip-verify` 시 스킵

서브에이전트 fresh context로 빌드/테스트/타입체크 실행.

실행: `/handoff-verify --once --skip-handoff` 스킬 호출.

- 실패 시 → 자동 수정 시도 (fixable 오류만) → 재검증
- 3회 실패 → 파이프라인 중단, 에러 보고

## 5단계: Sync Docs (문서 동기화)

> `--skip-docs` 시 스킵

변경 내용을 프로젝트 문서에 반영한다 (prompt_plan.md, spec.md, CLAUDE.md, rules/ 등).

실행: `/sync-docs` 스킬 호출.

## 6단계: 출하 (커밋 & 푸시 & 머지) — `--merge`/`--squash`/`--rebase` 있을 때만

> `MERGE=false`(머지 옵션 없음)이면 **이 단계를 건너뛰고 종료**.
> "검토 완료. 출하하려면 `--merge`를 붙여 다시 실행하세요." 출력.

`MERGE=true`이면 `/commit-push-pr` 스킬 호출.

전달 옵션:
- 커밋 메시지 (인자 또는 자동 생성)
- `--merge` / `--squash` / `--rebase` (사용자가 준 값 그대로)
- `--notify`
- `--no-verify` (이미 4단계에서 검증 완료 → 중복 빌드 스킵)

## 7단계: 다음 세션 프롬프트 — `--next-prompt` 있고 6단계(출하)가 성공했을 때만

> `--next-prompt`가 없거나 머지가 실행되지 않았으면 스킵.
> `--next-prompt`만 있고 머지 옵션이 없으면: "머지 옵션(--merge 등)과 함께 써야 합니다" 경고 후 스킵.

머지 직후의 상태를 기반으로, **새 세션에 그대로 붙여넣을 수 있는 시작 프롬프트**를 만든다.
목적: 컨텍스트 50% 규칙에 따라 세션을 끊고 새로 시작할 때, 다음 세션이 탐색 없이 바로 작업에 들어가게 한다.

### 수집 (이 세션이 이미 아는 것 + 최소 확인)

```bash
git log origin/main --oneline -3        # 머지 반영된 main HEAD
gh pr view <머지된 PR번호> --json title,url  # PR 링크
```

- 방금 머지한 PR: 번호·제목·핵심 변경 요약 (이 세션 컨텍스트에서)
- 다음 작업 후보: 우선순위 순으로 정리 — 출처는 ① PR 본문의 후속 체크리스트 ② prompt_plan.md/spec.md의 미완료 항목 ③ 이 세션에서 사용자와 합의한 다음 단계. 없으면 `/next-task` 스킬로 추천 생성
- 다음 세션이 먼저 읽어야 할 파일·메모리 포인터 (3~5개 이내, 확실한 것만)

### 산출

아래 형식의 프롬프트를 ① 채팅에 코드블록으로 출력하고 ② `.claude/next-session.md`에 저장(덮어쓰기)한다:

```markdown
# 이어서: <다음 작업 한 줄 제목>

## 직전 세션 결과 (머지 완료)
- PR #<N> "<제목>" → main 머지됨 (<merge 모드>)
- 핵심 변경: <2~3줄 요약>

## 현재 상태
- main HEAD: <sha> <제목>
- 검증: <테스트 수/빌드 상태 — 직전 세션 실측값>
- 주의: <다운그레이드 비호환, 미해결 이슈 등 있으면>

## 다음 작업 (우선순위 순)
1. <작업 1 — 구체적으로>
2. <작업 2>

## 먼저 읽을 것
- <파일 경로 or 메모리 이름> — <왜>

## 시작 지시
<첫 번째 행동을 지시하는 명령형 1~3문장. 계획 승인이 필요한 규모면 "계획 세워서 승인받고 시작해" 포함>
```

작성 규칙:
- **다음 세션은 이 프롬프트만 보고 시작한다**고 가정 — 이 세션의 은어·축약 금지, 경로·번호는 정확히
- 추측성 후보를 채우려고 늘리지 말 것 — 확실한 다음 작업이 1개면 1개만
- 마지막에 사용자에게 안내: "새 세션에서 위 프롬프트를 붙여넣거나 `.claude/next-session.md` 내용으로 시작하세요."

## 파이프라인 흐름도

```
/wrapup
  │
  ├─ 1. 사전 체크 (변경사항 확인)
  │
  ├─ 2. /refactor-clean (리팩토링 — 직접 수정)   ← --skip-refactor
  │
  ├─ 3. /code-review (보안+품질 — 보고)          ← --skip-review
  │     └─ CRITICAL → 중단
  │
  ├─ 4. /handoff-verify (빌드·테스트 — 검증)     ← --skip-verify
  │     └─ 실패 → 자동 수정 → 재검증 (최대 3회)
  │
  ├─ 5. /sync-docs (문서 동기화)                 ← --skip-docs
  │
  ├─ 6. [--merge/--squash/--rebase 있을 때만]
  │     /commit-push-pr (커밋 & 푸시 & 머지)
  │     └─ 없으면: 여기서 종료 (검토만)
  │
  └─ 7. [--next-prompt + 머지 성공 시에만]
        다음 세션 시작 프롬프트 생성
        └─ 채팅 출력 + .claude/next-session.md 저장
```

## 중단 조건

| 단계 | 중단 조건 | 복구 방법 |
|------|----------|----------|
| 1 | 변경사항 없음 | - |
| 2 | refactor 후 테스트 실패 | 자동 롤백 → 수동 수정 후 `/wrapup --skip-refactor` |
| 3 | CRITICAL 보안 이슈 | 수동 수정 후 `/wrapup --skip-refactor` |
| 4 | 빌드/테스트 3회 실패 | 에러 수정 후 `/wrapup --skip-refactor --skip-review` |

## 사용 예시

```bash
/wrapup                                   # 검토만: 리팩토링→리뷰→검증→문서동기화 (멈춤)
/wrapup --merge                           # 검토 + 출하(merge commit으로 머지)
/wrapup --squash --notify                 # 검토 + Squash 머지 + 알림
/wrapup feat: 기술인 목록 --merge          # 커밋 메시지 지정 + 출하
/wrapup --skip-docs                       # 문서 동기화만 빼고 검토
/wrapup --skip-refactor --skip-review --merge  # 검증만 + 즉시 출하 (빠른 모드)
/wrapup --merge --next-prompt             # 출하 후 다음 세션 시작 프롬프트까지 생성
/wrapup --squash --next-prompt --notify   # Squash 머지 + 알림 + 다음 세션 프롬프트
```
