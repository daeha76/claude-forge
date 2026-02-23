#!/bin/bash
# Email Guard - PreToolUse Hook
# Blocks mcp__gmail__send_email and redirects to draft_email
#
# Hook trigger: PreToolUse, matcher: mcp__gmail__send_email
# Exit codes: 0 = allow, 2 = block

# Read tool call JSON from stdin
INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null)

if [[ "$TOOL_NAME" == "mcp__gmail__send_email" ]]; then
    # Extract recipient for logging
    RECIPIENT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('to','unknown'))" 2>/dev/null)

    echo "BLOCKED: send_email to ${RECIPIENT}" >&2
    echo "Use mcp__gmail__draft_email instead. Review the draft before sending manually." >&2
    exit 2
fi

exit 0
