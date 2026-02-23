#!/bin/bash
# gemini-auto-review.sh - Stop Hook
# Claude 응답 완료 후, "Claude가 이번 세션에서 수정한 프론트엔드 파일"만 Gemini 리뷰
# gemini-collector.sh(PostToolUse)가 기록한 세션별 파일 목록을 참조
#
# 비활성화: touch ~/.claude/.no-gemini-review
# 재활성화: rm ~/.claude/.no-gemini-review

INPUT=$(cat)

# 0. 비활성화 플래그 확인
if [[ -f "$HOME/.claude/.no-gemini-review" ]]; then
    exit 0
fi

# 1. gemini CLI 존재 확인
if ! command -v gemini &>/dev/null; then
    exit 0
fi

# [H4] /tmp 파일 보안: 본인만 읽기/쓰기 가능하도록 제한
umask 077

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
TRACKER="/tmp/gemini-modified-${SESSION_ID}.txt"

if [[ ! -f "$TRACKER" || ! -s "$TRACKER" ]]; then
    exit 0
fi

# [L1] UUOC 제거: sort -u에 직접 파일 전달
MODIFIED_FILES=$(sort -u "$TRACKER")
FILE_COUNT=$(echo "$MODIFIED_FILES" | wc -l | tr -d ' ')

# 4. 각 파일의 diff 수집 (git 리포인 경우만)
# [H1] while IFS= read -r 로 공백 경로 안전 처리
FULL_DIFF=""
if git -C "$CWD" rev-parse --is-inside-work-tree &>/dev/null; then
    while IFS= read -r filepath; do
        [[ -z "$filepath" ]] && continue
        FILE_DIFF=$(git -C "$CWD" diff -U3 -- "$filepath" 2>/dev/null || true)
        STAGED_DIFF=$(git -C "$CWD" diff --cached -U3 -- "$filepath" 2>/dev/null || true)
        FULL_DIFF="${FULL_DIFF}${FILE_DIFF}${STAGED_DIFF}"
    done <<< "$MODIFIED_FILES"
fi

# git 리포가 아니거나 diff가 없으면 파일 내용 직접 읽기
if [[ -z "$FULL_DIFF" ]]; then
    while IFS= read -r filepath; do
        [[ -z "$filepath" ]] && continue
        if [[ -f "$filepath" ]]; then
            FULL_DIFF="${FULL_DIFF}
--- ${filepath} ---
$(head -200 "$filepath" 2>/dev/null || true)
"
        fi
    done <<< "$MODIFIED_FILES"
fi

if [[ -z "$FULL_DIFF" ]]; then
    exit 0
fi

# 5. [C3] 시크릿 패턴 필터링 (Google 서버 전송 전)
# diff에 포함된 API 키, 토큰, 비밀번호 등을 마스킹
FULL_DIFF=$(echo "$FULL_DIFF" | sed -E \
    -e 's/(OPENAI_API_KEY|SUPABASE_KEY|SUPABASE_SERVICE_ROLE_KEY|ANTHROPIC_API_KEY|SECRET_KEY|PASSWORD|TOKEN|API_KEY|PRIVATE_KEY|DATABASE_URL|REDIS_URL)=['"'"'"]?[^'"'"'" \n]+['"'"'"]?/\1=[REDACTED]/gi' \
    -e 's/sk-[a-zA-Z0-9]{20,}/[REDACTED_SK_KEY]/g' \
    -e 's/ghp_[a-zA-Z0-9]{36,}/[REDACTED_GHP]/g' \
    -e 's/gho_[a-zA-Z0-9]{36,}/[REDACTED_GHO]/g' \
    -e 's/xoxb-[a-zA-Z0-9-]+/[REDACTED_SLACK]/g' \
    -e 's/eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/[REDACTED_JWT]/g')

# 6. diff 해시로 중복 리뷰 방지
HASH_FILE="/tmp/gemini-review-last-hash-${SESSION_ID}"
CURRENT_HASH=$(printf '%s' "$FULL_DIFF" | shasum -a 256 | cut -d' ' -f1)

if [[ -f "$HASH_FILE" ]] && [[ "$(cat "$HASH_FILE" 2>/dev/null)" == "$CURRENT_HASH" ]]; then
    exit 0
fi

# 7. diff 크기 확인 (100KB 제한)
DIFF_SIZE=$(printf '%s' "$FULL_DIFF" | wc -c | tr -d ' ')
if [[ "$DIFF_SIZE" -gt 102400 ]]; then
    echo '{"systemMessage":"[Gemini Frontend-Review] 변경량이 100KB 초과. gemini-reviewer 에이전트로 수동 실행하세요."}'
    exit 0
fi

# 8. [H5] 모델명 환경변수화 (기본값: gemini-3-pro-preview)
GEMINI_MODEL="${GEMINI_MODEL:-gemini-3-pro-preview}"

# 9. [H2/M3] 프롬프트를 mktemp 임시파일로 전달 (ARG_MAX 초과 방지 + symlink 방지)
PROMPT_FILE=$(mktemp /tmp/gemini-prompt-XXXXXX.txt)
# [L2] 종료 시 임시파일 정리
trap 'rm -f "$PROMPT_FILE"' EXIT

cat > "$PROMPT_FILE" <<PROMPT_EOF
다음 프론트엔드 코드 변경을 리뷰해줘.
CRITICAL 또는 HIGH 심각도 이슈만 보고해줘.
이슈가 없으면 '이슈 없음'만 출력.

6대 프론트엔드 카테고리로 분석:
1. React/Next.js 패턴: 서버/클라이언트 컴포넌트 구분, useEffect 의존성, 'use client' 남용
2. 접근성(a11y): alt 텍스트, label, ARIA, 키보드 네비게이션
3. 성능: useMemo/useCallback 남용 vs 누락, 불필요한 리렌더링
4. CSS/Tailwind: 클래스 순서, 반응형 일관성, 다크모드
5. 번들 크기: 전체 라이브러리 import, tree-shaking 방해
6. 보안: dangerouslySetInnerHTML, XSS

각 이슈 형식:
- [심각도] 파일:라인 - 설명 (제안)

한국어로 간결하게 답변.

${FULL_DIFF}
PROMPT_EOF

# 10. Gemini 리뷰 실행 (프롬프트를 cat으로 읽어서 -p에 전달)
REVIEW=$(gemini -p "$(cat "$PROMPT_FILE")" \
    -m "$GEMINI_MODEL" \
    -o json 2>/dev/null || true)

# [C1] JSON에서 response 추출: here-string으로 전달 (pipe의 seek(0) 실패 방지)
REVIEW_TEXT=$(python3 -c "
import sys, json
raw = sys.stdin.read()
try:
    d = json.loads(raw)
    print(d.get('response', ''))
except:
    print(raw)
" <<< "$REVIEW" 2>/dev/null)

# 11. 결과 확인
if [[ -z "$REVIEW_TEXT" ]]; then
    exit 0
fi

# 12. 해시 저장 (리뷰 성공 시만)
printf '%s' "$CURRENT_HASH" > "$HASH_FILE"

# 13. "이슈 없음"이면 조용히 종료
if echo "$REVIEW_TEXT" | grep -qi "이슈 없음\|no issues\|looks good\|no critical\|no high"; then
    exit 0
fi

# 14. [C2/H3] 이슈 발견 시 Claude에게 피드백 (python3으로 안전한 JSON 생성)
# 환경변수로 전달 + 쿼팅된 heredoc으로 쉘 삽입/트리플쿼트 깨짐 방지
FILE_LIST_DISPLAY=$(echo "$MODIFIED_FILES" | tr '\n' ', ' | sed 's/,$//')

GEMINI_REVIEW="$REVIEW_TEXT" \
GEMINI_FILE_LIST="$FILE_LIST_DISPLAY" \
GEMINI_FILE_COUNT="$FILE_COUNT" \
python3 <<'PYEOF'
import json, os

review_text = os.environ.get('GEMINI_REVIEW', '')
file_list = os.environ.get('GEMINI_FILE_LIST', '')
file_count = os.environ.get('GEMINI_FILE_COUNT', '0')

# [H3] 리뷰 결과 길이 제한 (프롬프트 인젝션 완화)
sanitized = review_text[:5000]

msg = (
    f"[Gemini Frontend-Review] Claude가 수정한 {file_count}개 프론트엔드 파일 리뷰 결과:\n"
    f"파일: {file_list}\n\n"
    f"{sanitized}\n\n"
    f"위 CRITICAL/HIGH 이슈 중 Fixable 항목은 즉시 수정하세요. Non-Fixable 이슈만 사용자에게 보고하세요."
)

output = {"continue": True, "systemMessage": msg}
print(json.dumps(output, ensure_ascii=False))
PYEOF

exit 0
