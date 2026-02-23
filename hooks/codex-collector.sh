#!/bin/bash
# codex-collector.sh - PostToolUse Hook (Edit/Write)
# Claude가 Edit/Write로 수정한 코드 파일 경로를 세션별 파일에 기록
# Stop 훅(codex-auto-review.sh)이 이 파일을 읽어서 리뷰 대상 결정
# exit 0 필수 (세션 방해 금지)

INPUT=$(cat)

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

# 코드 파일만 기록 (CODEX_TRACK_ALL 설정 시 설정 파일 확장자도 포함)
if [[ -n "$CODEX_TRACK_ALL" ]]; then
    case "$FILE_PATH" in
        *.ts|*.tsx|*.js|*.jsx|*.py|*.go|*.rs|*.java|*.rb|*.php|*.swift|*.kt|*.dart|*.vue|*.svelte|*.sh|*.md|*.json|*.yaml|*.toml)
            ;;
        *)
            exit 0
            ;;
    esac
else
    case "$FILE_PATH" in
        *.ts|*.tsx|*.js|*.jsx|*.py|*.go|*.rs|*.java|*.rb|*.php|*.swift|*.kt|*.dart|*.vue|*.svelte|*.sh)
            ;;
        *)
            exit 0
            ;;
    esac
fi

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
TRACKER="/tmp/codex-modified-${SESSION_ID}.txt"
if ! grep -qxF "$FILE_PATH" "$TRACKER" 2>/dev/null; then
    echo "$FILE_PATH" >> "$TRACKER"
fi

exit 0
