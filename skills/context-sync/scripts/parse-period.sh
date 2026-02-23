#!/usr/bin/env bash
# parse-period.sh - 기간 문자열을 파싱하여 시작 시간을 ISO 8601로 출력
# Usage: bash parse-period.sh "24h"
# Output: 2026-02-21T10:00:00 (현재 시간에서 24시간 전)

set -uo pipefail

PERIOD="${1:-24h}"

# 숫자와 단위 분리
NUM=$(echo "$PERIOD" | grep -oE '[0-9]+')
UNIT=$(echo "$PERIOD" | grep -oE '[a-zA-Z]+')

# 기본값: 숫자만 입력 시 시간(h)으로 간주
if [ -z "$UNIT" ]; then
  UNIT="h"
fi

if [ -z "$NUM" ]; then
  echo "Error: Invalid period format '$PERIOD'. Use Nh or Nd (e.g., 24h, 7d)" >&2
  exit 1
fi

case "$UNIT" in
  h|H|hour|hours)
    # macOS date: N시간 전
    START=$(date -j -v-"${NUM}"H '+%Y-%m-%dT%H:%M:%S' 2>/dev/null)
    if [ $? -ne 0 ]; then
      # Linux fallback
      START=$(date -d "-${NUM} hours" '+%Y-%m-%dT%H:%M:%S' 2>/dev/null)
    fi
    ;;
  d|D|day|days)
    # macOS date: N일 전
    START=$(date -j -v-"${NUM}"d '+%Y-%m-%dT%H:%M:%S' 2>/dev/null)
    if [ $? -ne 0 ]; then
      # Linux fallback
      START=$(date -d "-${NUM} days" '+%Y-%m-%dT%H:%M:%S' 2>/dev/null)
    fi
    ;;
  *)
    echo "Error: Unknown unit '$UNIT'. Use h (hours) or d (days)." >&2
    exit 1
    ;;
esac

if [ -z "$START" ]; then
  echo "Error: Failed to calculate start time." >&2
  exit 1
fi

NOW=$(date '+%Y-%m-%dT%H:%M:%S')

echo "{\"start\":\"$START\",\"end\":\"$NOW\",\"period\":\"$PERIOD\"}"
