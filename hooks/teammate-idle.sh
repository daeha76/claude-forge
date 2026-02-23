#!/bin/bash
# Teammate Idle Monitor - TeammateIdle Hook
# 팀원이 idle 상태로 전환될 때 로깅
#
# Hook trigger: TeammateIdle
# Exit codes: 0 = idle 허용, 2 = 계속 작업 (stderr로 피드백)

# Read hook input JSON from stdin
INPUT=$(cat)

echo "$INPUT" | python3 -c "
import sys, json

try:
    data = json.load(sys.stdin)
except:
    sys.exit(0)

session_id = data.get('session_id', 'unknown')
teammate = data.get('teammate_name', 'unknown')
team = data.get('team_name', 'unknown')

print(f'[teammate-idle] {teammate} idle (team: {team}, session: {session_id})', file=sys.stderr)
" 2>/dev/null

exit 0
