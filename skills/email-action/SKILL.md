---
name: email-action
description: 이메일 전송 워크플로우. 사용자가 이메일을 보내달라고 요청하거나, "/email-action" 트리거 시 활성화. clarify(의도 확인) → draft(초안) → preview(미리보기) → approve(승인 → 전송)의 4단계로 안전하게 이메일을 발송한다. mcp__gmail 도구를 사용하여 실제 전송.
---

# Email Action

이메일 전송을 4단계 워크플로우로 안전하게 처리한다.

## Related Files

| File | Purpose | When to Read |
|------|---------|--------------|
| [~/.claude/skills/_reference/clarify-before-action.md](~/.claude/skills/_reference/clarify-before-action.md) | 외부 액션 전 의도 확인 패턴 (WCTU) | 이메일 전송 전 clarify 단계 수행 시 |
| [~/.claude/skills/_reference/output-quality.md](~/.claude/skills/_reference/output-quality.md) | 출력 품질 기준 (한국어, 결론 먼저 등) | 이메일 초안 작성 시 |

## 워크플로우

```
/email-action <의도 설명>

Phase 1: Clarify → Phase 2: Draft → Phase 3: Preview → Phase 4: Approve
```

### Phase 1: Clarify (의도 확인)

위험도를 판정하고 적절한 확인 흐름을 선택한다.

**위험도 판정** (clarify-before-action.md 참조):
- 수신자(내부/외부), 내용(일상/민감), 빈도(반복/최초)를 평가
- 모든 차원 낮음 → 간소화 확인
- 하나라도 높음 → 단계별 확인

**간소화 확인** (위험도 낮음):

```
이메일 전송을 준비합니다.

수신자: {추론된 이메일}
목적: {추론된 목적}
톤: {추론된 톤}

이 방향으로 진행할까요? (진행 / 수정 / 취소)
```

**단계별 확인** (위험도 높음):

```
[Step 1: Who] 수신자 확인
- 메인 수신자: {이메일}
- CC/BCC 추가할 분이 있나요?

[Step 2: Context + Tone] 맥락/톤 확인
- 목적: {목적}
- 톤: {공식/비공식}
- 길이: {간결/상세}
- 이 방향이 맞나요?
```

**--skip-clarify 옵션**: 사용자가 명시적으로 지정하면 Phase 1을 건너뛰고 Phase 2로 직행. 단, Phase 3(미리보기)와 Phase 4(승인)는 스킵 불가.

### Phase 2: Draft (초안 작성)

Phase 1에서 확인한 정보를 기반으로 이메일 초안을 작성한다.

**작성 규칙**:
- 수신자의 언어/문화에 맞는 표현 사용
- Phase 1에서 확정한 톤과 길이 준수
- 제목은 명확하고 간결하게 (50자 이내)
- 본문은 결론 먼저 → 상세 순서

### Phase 3: Preview (미리보기)

전체 이메일을 미리보기 형태로 표시한다. 이 단계는 **생략 불가**.

```
[이메일 미리보기]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
수신자: {to}
CC: {cc 또는 없음}
BCC: {bcc 또는 없음}
제목: {subject}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{body}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

수정할 부분이 있나요? (전송 / 수정 / 취소)
```

수정 요청 시 해당 부분만 수정 후 다시 미리보기를 표시한다.

### Phase 4: Approve (승인 → 전송)

사용자가 "전송"을 선택하면 mcp__gmail 도구로 실제 전송한다.

```
이메일을 전송했습니다.
수신자: {to}
제목: {subject}
시각: {전송 시각}
```

전송 실패 시 에러 내용을 표시하고 재시도/취소 선택지를 제공한다.

## 주의사항

- Phase 3(미리보기)와 Phase 4(최종 승인)는 어떤 경우에도 생략 불가
- 외부 수신자(고객, 파트너)에게 보내는 이메일은 반드시 단계별 확인 (흐름 2) 사용
- 첨부파일이 있는 경우 파일명과 크기를 미리보기에 포함
- 여러 수신자에게 동시 발송 시 각 수신자 목록을 명시적으로 표시
