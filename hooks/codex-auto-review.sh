#!/bin/bash
# codex-auto-review.sh - Stop Hook
# Claude 응답 완료 후, "Claude가 이번 세션에서 수정한 코드 파일"만 Codex 리뷰
# codex-collector.sh(PostToolUse)가 기록한 세션별 파일 목록을 참조
#
# 비활성화: touch ~/.claude/.no-codex-review
# 재활성화: rm ~/.claude/.no-codex-review

INPUT=$(cat)

# 0. 비활성화 플래그 확인
if [[ -f "$HOME/.claude/.no-codex-review" ]]; then
    exit 0
fi

# 1. codex CLI 존재 확인
if ! command -v codex &>/dev/null; then
    exit 0
fi

# 2. 세션 ID와 작업 디렉토리 추출
read -r SESSION_ID CWD < <(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    sid = d.get('session_id', '')
    cwd = d.get('cwd', '')
    print(f'{sid} {cwd}')
except:
    print(' ')
" 2>/dev/null)

if [[ -z "$SESSION_ID" || -z "$CWD" ]]; then
    exit 0
fi

# 3. 세션별 수정 파일 목록 확인 (collector가 기록한 것)
TRACKER="/tmp/codex-modified-${SESSION_ID}.txt"

if [[ ! -f "$TRACKER" || ! -s "$TRACKER" ]]; then
    # Claude가 이번 세션에서 코드 파일을 수정하지 않음 → 종료
    exit 0
fi

MODIFIED_FILES=$(cat "$TRACKER" | sort -u)
FILE_COUNT=$(echo "$MODIFIED_FILES" | wc -l | tr -d ' ')

# 4. 각 파일의 diff 수집 (git 리포인 경우만)
FULL_DIFF=""
if git -C "$CWD" rev-parse --is-inside-work-tree &>/dev/null; then
    for filepath in $MODIFIED_FILES; do
        FILE_DIFF=$(git -C "$CWD" diff -U3 -- "$filepath" 2>/dev/null || true)
        STAGED_DIFF=$(git -C "$CWD" diff --cached -U3 -- "$filepath" 2>/dev/null || true)
        FULL_DIFF="${FULL_DIFF}${FILE_DIFF}${STAGED_DIFF}"
    done
fi

# git 리포가 아니거나 diff가 없으면 파일 내용 직접 읽기
if [[ -z "$FULL_DIFF" ]]; then
    for filepath in $MODIFIED_FILES; do
        if [[ -f "$filepath" ]]; then
            FULL_DIFF="${FULL_DIFF}
--- ${filepath} ---
$(head -200 "$filepath" 2>/dev/null || true)
"
        fi
    done
fi

if [[ -z "$FULL_DIFF" ]]; then
    exit 0
fi

# 5. diff 해시로 중복 리뷰 방지
HASH_FILE="/tmp/codex-review-last-hash-${SESSION_ID}"
CURRENT_HASH=$(echo "$FULL_DIFF" | shasum -a 256 | cut -d' ' -f1)

if [[ -f "$HASH_FILE" ]] && [[ "$(cat "$HASH_FILE" 2>/dev/null)" == "$CURRENT_HASH" ]]; then
    exit 0
fi

# 6. diff 크기 확인 (100KB 제한)
DIFF_SIZE=$(echo "$FULL_DIFF" | wc -c | tr -d ' ')
if [[ "$DIFF_SIZE" -gt 102400 ]]; then
    echo '{"systemMessage":"[Codex Auto-Review] 변경량이 100KB 초과. /codex-review로 수동 실행하세요."}'
    exit 0
fi

# 7. Codex 리뷰 실행
RESULT_FILE="/tmp/codex-review-result-$$.txt"
trap "rm -f '$RESULT_FILE'" EXIT

codex exec \
    --skip-git-repo-check \
    --sandbox read-only \
    --ephemeral \
    -o "$RESULT_FILE" \
    - <<EOF 2>/dev/null || true
다음 코드 변경을 리뷰해줘.
CRITICAL 또는 HIGH 심각도 이슈만 보고해줘.
이슈가 없으면 "이슈 없음"만 출력.

각 이슈 형식:
- [심각도] 파일:라인 - 설명 (제안)

한국어로 간결하게 답변.

$FULL_DIFF
EOF

# 8. 결과 확인
if [[ ! -f "$RESULT_FILE" ]] || [[ ! -s "$RESULT_FILE" ]]; then
    exit 0
fi

REVIEW=$(cat "$RESULT_FILE")

# 9. 해시 저장 (리뷰 성공 시만)
echo "$CURRENT_HASH" > "$HASH_FILE"

# 10. "이슈 없음"이면 조용히 종료
if echo "$REVIEW" | grep -qi "이슈 없음\|no issues\|looks good\|no critical\|no high"; then
    exit 0
fi

# 11. 이슈 발견 시 Claude에게 피드백 + 자동 계속
FILE_LIST_DISPLAY=$(echo "$MODIFIED_FILES" | tr '\n' ', ' | sed 's/,$//')
ESCAPED_REVIEW=$(python3 -c "
import sys, json
review = sys.stdin.read()
print(json.dumps(review))
" <<< "$REVIEW" 2>/dev/null || echo "\"리뷰 결과 파싱 실패\"")

cat <<ENDJSON
{
  "continue": true,
  "systemMessage": "[Codex Auto-Review] Claude가 수정한 ${FILE_COUNT}개 코드 파일 리뷰 결과:\n파일: ${FILE_LIST_DISPLAY}\n\n${ESCAPED_REVIEW}\n\n위 CRITICAL/HIGH 이슈 중 Fixable 항목은 즉시 수정하세요. Non-Fixable 이슈만 사용자에게 보고하세요."
}
ENDJSON

exit 0
