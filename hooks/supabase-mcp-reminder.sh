#!/bin/bash
# Supabase SQL 관련 명령어 감지 시 MCP 사용 안내

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null)

# Supabase SQL 관련 명령어 패턴 감지
if echo "$COMMAND" | grep -qiE "(supabase.*db|supabase.*migration|psql|CREATE TABLE|ALTER TABLE|DROP TABLE|INSERT INTO|UPDATE.*SET|DELETE FROM)"; then

  # MCP 사용 안내 메시지 출력 (stderr로 사용자에게 표시)
  cat >&2 << 'EOF'
════════════════════════════════════════════════════════════════
  Supabase SQL 작업 감지

Supabase MCP 도구 사용을 권장합니다:
  * mcp__supabase__execute_sql - SQL 실행
  * mcp__supabase__apply_migration - 마이그레이션 적용
  * mcp__supabase__list_tables - 테이블 목록
  * mcp__supabase__get_advisors - 보안/성능 검사

ToolSearch로 먼저 도구를 로드하세요:
  ToolSearch query: "+supabase sql"

계속 진행하려면 승인하세요.
════════════════════════════════════════════════════════════════
EOF

fi

# 항상 허용 (안내만 표시, 차단하지 않음)
exit 0
