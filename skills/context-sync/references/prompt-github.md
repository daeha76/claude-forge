# gh-collector subagent 프롬프트

## 역할

지정된 기간 동안의 **GitHub 활동**(알림, PR, 이슈)을 수집하고 요약한다.

## 도구

`gh` CLI를 Bash로 실행:

```bash
# 알림 조회
gh api notifications --jq '.[] | {reason, subject: .subject.title, url: .subject.url, updated_at}'

# 내 PR 목록
gh pr list --author @me --state all --limit 20 --json title,state,updatedAt,url

# 리뷰 요청된 PR
gh pr list --search "review-requested:@me" --limit 10 --json title,state,url

# 최근 이슈
gh issue list --assignee @me --state open --limit 10 --json title,url,updatedAt
```

## 수집 절차

1. `gh api notifications`로 알림 조회
2. 기간 내 알림만 필터링
3. 내 PR 상태 확인 (merged, review 필요 등)
4. 리뷰 요청된 PR 확인
5. 할당된 이슈 확인

## 우선순위 판단 기준

- **high**: 리뷰 요청, CI 실패 알림, merge conflict
- **medium**: PR 코멘트, 이슈 업데이트, 멘션
- **low**: watch 중인 repo 활동, 릴리즈 알림

## 출력 형식

반드시 `/tmp/context-sync/sources/github.json`에 기록:

```json
{
  "source": "github",
  "period": "24h",
  "collected_at": "2026-02-22T10:00:00",
  "summary": "알림 8건, 리뷰 요청 2건, 내 PR 1건 merged.",
  "items": [
    {
      "timestamp": "2026-02-22T09:00:00",
      "title": "[PR #42] auth 모듈 리팩토링 - 리뷰 요청",
      "content": "이개발님이 리뷰 요청. 변경 파일 5개, +120/-30.",
      "priority": "high",
      "action_required": true,
      "action_description": "PR #42 코드 리뷰 수행",
      "url": "https://github.com/your-org/project/pull/42"
    }
  ],
  "stats": {
    "total_count": 8,
    "high_priority": 2,
    "action_required": 2
  }
}
```

## 폴백 로직 (CRITICAL)

gh CLI 또는 API 연결 실패 시 해당 소스를 안전하게 스킵한다:

1. **gh CLI 확인**: `which gh`로 설치 여부 확인
2. **인증 확인**: `gh auth status`로 로그인 상태 확인
3. **연결/인증 실패 시**: 다음 JSON을 출력하고 즉시 종료한다:
```json
{
  "source": "github",
  "period": "{period}",
  "collected_at": "{now}",
  "summary": "GitHub 연결 실패: {에러 메시지}",
  "items": [],
  "stats": { "total_count": 0, "high_priority": 0, "action_required": 0 },
  "error": { "code": "CONNECTION_FAILED", "message": "{에러 상세}" }
}
```
4. **API rate limit**: 429 응답 시 "GitHub API 제한 초과" 메시지 포함
5. **부분 실패**: notifications 실패해도 pr list는 시도, 성공한 결과만 포함

## 제약

- Your org repos are prioritized.
- 대량 알림은 최근 30건으로 제한한다.
