#!/bin/bash
# Calendar Guard - PreToolUse Hook
# Warns before creating calendar events (does not block)
#
# Hook trigger: PreToolUse, matcher: mcp__google-calendar__create-event
# Exit codes: 0 = allow (warning only, never blocks)

# Read tool call JSON from stdin
INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null)

if [[ "$TOOL_NAME" == "mcp__google-calendar__create-event" ]]; then
    SUMMARY=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('summary','unknown'))" 2>/dev/null)

    cat >&2 << EOF
════════════════════════════════════════════════════════════════
  Google Calendar 이벤트 생성 감지

  이벤트: ${SUMMARY}

  캘린더에 새 일정이 추가됩니다. 내용을 확인하세요.
  계속 진행하려면 승인하세요.
════════════════════════════════════════════════════════════════
EOF
fi

exit 0
