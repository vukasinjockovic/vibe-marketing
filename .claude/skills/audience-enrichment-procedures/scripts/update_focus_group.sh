#!/usr/bin/env bash
# update_focus_group.sh -- Convex CLI wrapper for focusGroups:enrich
#
# Usage:
#   update_focus_group.sh <focus_group_id> <fields_json> <agent_name> <reasoning>
#
# Example:
#   update_focus_group.sh "k17abc123" '{"awarenessStage":"problem_aware","awarenessConfidence":"high"}' \
#     "vibe-audience-enricher" "Matched 4 indicators for problem_aware"
#
# Requires:
#   - CONVEX_URL env var (defaults to http://localhost:3210)
#   - CONVEX_SELF_HOSTED_ADMIN_KEY env var (optional, for admin access)

set -euo pipefail

# Load env if available
source .env 2>/dev/null || true
source .env.local 2>/dev/null || true

CONVEX_URL="${CONVEX_URL:-http://localhost:3210}"
ADMIN_KEY="${CONVEX_SELF_HOSTED_ADMIN_KEY:-}"

if [ $# -lt 4 ]; then
  echo "Usage: update_focus_group.sh <focus_group_id> <fields_json> <agent_name> <reasoning>" >&2
  exit 1
fi

FG_ID="$1"
FIELDS_JSON="$2"
AGENT_NAME="$3"
REASONING="$4"

# Escape reasoning for JSON (handle quotes and newlines)
ESCAPED_REASONING=$(printf '%s' "$REASONING" | sed 's/"/\\"/g' | tr '\n' ' ')

ARGS="{\"id\":\"$FG_ID\",\"fields\":$FIELDS_JSON,\"agentName\":\"$AGENT_NAME\",\"reasoning\":\"$ESCAPED_REASONING\"}"

if [ -n "$ADMIN_KEY" ]; then
  npx convex run focusGroups:enrich "$ARGS" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY"
else
  npx convex run focusGroups:enrich "$ARGS" --url "$CONVEX_URL"
fi
