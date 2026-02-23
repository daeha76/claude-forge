#!/bin/bash
# gemini-collector.sh - PostToolUse Hook (Edit/Write)
# Claude가 Edit/Write로 수정한 프론트엔드 파일 경로를 세션별 파일에 기록
# Stop 훅(gemini-auto-review.sh)이 이 파일을 읽어서 리뷰 대상 결정
# 프론트엔드 파일만 수집: tsx, jsx, css, scss, html, vue, svelte
# .ts 파일은 의도적 제외 — 프론트엔드 "템플릿" 파일만 대상 (순수 TS 로직은 codex-reviewer 범위)
# exit 0 필수 (세션 방해 금지)

INPUT=$(cat)

# [H4] /tmp 파일 보안: 본인만 읽기/쓰기
umask 077

# 파일 경로 추출
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    inp = d.get('tool_input', {})
    print(inp.get('file_path', ''))
except:
    pass
" 2>/dev/null)

if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

# 프론트엔드 파일만 기록
case "$FILE_PATH" in
    *.tsx|*.jsx|*.css|*.scss|*.html|*.vue|*.svelte)
        ;;
    *)
        exit 0
        ;;
esac

# 세션 ID 추출
SESSION_ID=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('session_id', 'unknown'))
except:
    print('unknown')
" 2>/dev/null)

# 세션별 파일에 경로 추가 (중복 방지)
TRACKER="/tmp/gemini-modified-${SESSION_ID}.txt"
if ! grep -qxF "$FILE_PATH" "$TRACKER" 2>/dev/null; then
    echo "$FILE_PATH" >> "$TRACKER"
fi

exit 0
