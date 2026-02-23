#!/bin/bash
# Ads Guard - PreToolUse Hook
# Blocks write operations on ad platforms (Meta Ads, Google Ads)
# Allows read-only operations (get_insights, list_campaigns, etc.)
#
# Hook trigger: PreToolUse, matcher: mcp__meta-ads__*, mcp__google-ads-mcp__*
# Exit codes: 0 = allow, 2 = block

# Read tool call JSON from stdin
INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null)

# Define read-only (safe) tool patterns
SAFE_PATTERNS=(
    "get_insights"
    "list_campaigns"
    "list_adsets"
    "list_ads"
    "get_campaign"
    "get_adset"
    "get_ad"
    "compare_performance"
    "search"
    "list_accessible_customers"
    "get_account"
)

# Check if the tool matches a safe pattern
for pattern in "${SAFE_PATTERNS[@]}"; do
    if [[ "$TOOL_NAME" == *"$pattern"* ]]; then
        exit 0
    fi
done

# Block any write/modify operations
echo "BLOCKED: Ad platform write operation not allowed: ${TOOL_NAME}" >&2
echo "Only read-only operations (get_insights, list_campaigns, search, etc.) are permitted." >&2
echo "Request user approval for campaign modifications." >&2
exit 2
