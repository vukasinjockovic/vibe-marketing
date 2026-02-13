#!/usr/bin/env bash
# Usage: ./scripts/invoke-agent.sh <agent-name> <task-id>
#        ./scripts/invoke-agent.sh <agent-name> <task-id> --branch <label>
#        ./scripts/invoke-agent.sh <agent-name> --heartbeat
#
# Examples:
#   ./scripts/invoke-agent.sh vibe-content-writer abc123
#   ./scripts/invoke-agent.sh vibe-image-director abc123 --branch "Hero Image"
#   ./scripts/invoke-agent.sh vibe-audience-enricher --heartbeat
#
# Invokes a Claude Code agent for a specific task, handling:
# - Skill path resolution via Convex agent registry (fallback: .claude/skills/<name>)
# - Lock acquisition and release (pipeline mode)
# - Branch label tracking and completeBranch call (branch mode)
# - Agent run tracking via analytics
# - Activity logging on failure
# - Log capture to logs/ directory
# - Heartbeat mode for scheduled agents (no task ID needed)

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 <agent-name> <task-id>"
  echo "       $0 <agent-name> <task-id> --branch <label>"
  echo "       $0 <agent-name> --heartbeat"
  exit 1
fi

AGENT_NAME="$1"
MODE="pipeline"
TASK_ID=""
BRANCH_LABEL=""

if [ "$2" = "--heartbeat" ]; then
  MODE="heartbeat"
else
  TASK_ID="$2"
fi

# Check for --branch flag
if [ $# -ge 4 ] && [ "$3" = "--branch" ]; then
  MODE="branch"
  BRANCH_LABEL="$4"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load env
set -a
source "$PROJECT_DIR/.env"
set +a

CONVEX_URL="${CONVEX_SELF_HOSTED_URL:-http://localhost:3210}"
ADMIN_KEY="${CONVEX_SELF_HOSTED_ADMIN_KEY}"

# Resolve skill directory from Convex agent registry, fallback to convention
SKILL_PATH=""
AGENT_RECORD=$(npx convex run agents:getByName "{\"name\":\"${AGENT_NAME}\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || echo "")
if [ -n "$AGENT_RECORD" ] && echo "$AGENT_RECORD" | grep -q '"skillPath"'; then
  SKILL_PATH=$(echo "$AGENT_RECORD" | python3 -c "import sys,json; print(json.load(sys.stdin).get('skillPath',''))" 2>/dev/null || echo "")
fi

if [ -z "$SKILL_PATH" ]; then
  SKILL_PATH=".claude/skills/${AGENT_NAME}"
fi

SKILL_DIR="$PROJECT_DIR/$SKILL_PATH"

# Check skill exists
if [ ! -d "$SKILL_DIR" ]; then
  echo "ERROR: Skill directory not found: $SKILL_DIR"
  npx convex run activities:log "{\"type\":\"error\",\"agentName\":\"${AGENT_NAME}\",\"message\":\"Skill directory not found: ${SKILL_DIR}\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true
  exit 1
fi

# Ensure logs and stream directories exist
mkdir -p "$PROJECT_DIR/logs"
mkdir -p /tmp/vibe-streams

# Log agent run start
npx convex run analytics:startRun "{\"agentName\":\"${AGENT_NAME}\",\"model\":\"sonnet\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true

# Update agent heartbeat
npx convex run agents:heartbeat "{\"name\":\"${AGENT_NAME}\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true

if [ "$MODE" = "pipeline" ]; then
  # Acquire lock
  LOCK_RESULT=$(npx convex run pipeline:acquireLock "{\"taskId\":\"${TASK_ID}\",\"agentName\":\"${AGENT_NAME}\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null)
  if echo "$LOCK_RESULT" | grep -q '"acquired":false'; then
    echo "WARN: Could not acquire lock on task $TASK_ID"
    exit 1
  fi

  # Log agent start activity
  npx convex run activities:log "{\"type\":\"info\",\"agentName\":\"${AGENT_NAME}\",\"taskId\":\"${TASK_ID}\",\"message\":\"Agent invoked for task\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true

  # Invoke Claude Code for pipeline task
  LOG_FILE="$PROJECT_DIR/logs/${AGENT_NAME}-$(date +%Y%m%d-%H%M%S).log"
  STREAM_FILE="/tmp/vibe-streams/${TASK_ID}.jsonl"
  cd "$PROJECT_DIR"

  # Clean up stream file on exit
  trap 'rm -f "$STREAM_FILE"' EXIT

  PROMPT="You are ${AGENT_NAME}. Task ID: ${TASK_ID}. Convex URL: ${CONVEX_URL}. Read your SKILL.md, check your WORKING memory, query the task from Convex, and execute your work. When done, call pipeline:completeStep."
  claude -p "$PROMPT" \
    --dangerously-skip-permissions \
    --verbose \
    --output-format stream-json \
    2>"$LOG_FILE" | tee "$STREAM_FILE" >> "$LOG_FILE"

  EXIT_CODE=${PIPESTATUS[0]}

  # Log result
  if [ $EXIT_CODE -ne 0 ]; then
    # Agent crashed — release lock and log error
    npx convex run pipeline:releaseLock "{\"taskId\":\"${TASK_ID}\",\"agentName\":\"${AGENT_NAME}\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true
    npx convex run activities:log "{\"type\":\"error\",\"agentName\":\"${AGENT_NAME}\",\"taskId\":\"${TASK_ID}\",\"message\":\"Agent crashed with exit code ${EXIT_CODE}\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true
    npx convex run notifications:create "{\"mentionedAgent\":\"@human\",\"fromAgent\":\"${AGENT_NAME}\",\"taskId\":\"${TASK_ID}\",\"content\":\"Agent ${AGENT_NAME} crashed (exit ${EXIT_CODE})\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true
    # TODO:NOTIFICATION_PREFERENCES — Agent crash Telegram notification
    python3 "$SCRIPT_DIR/notify.py" "💥 Agent ${AGENT_NAME} crashed (exit ${EXIT_CODE}) on task ${TASK_ID}" 2>/dev/null || true
  else
    # Agent completed successfully
    npx convex run activities:log "{\"type\":\"complete\",\"agentName\":\"${AGENT_NAME}\",\"taskId\":\"${TASK_ID}\",\"message\":\"Agent completed successfully\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true
  fi

elif [ "$MODE" = "branch" ]; then
  # Branch mode — no lock, agent runs for a specific branch deliverable
  npx convex run activities:log "{\"type\":\"info\",\"agentName\":\"${AGENT_NAME}\",\"taskId\":\"${TASK_ID}\",\"message\":\"Branch agent invoked for: ${BRANCH_LABEL}\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true

  LOG_FILE="$PROJECT_DIR/logs/${AGENT_NAME}-branch-$(date +%Y%m%d-%H%M%S).log"
  STREAM_FILE="/tmp/vibe-streams/${TASK_ID}-branch-${AGENT_NAME}.jsonl"
  cd "$PROJECT_DIR"

  trap 'rm -f "$STREAM_FILE"' EXIT

  PROMPT="You are ${AGENT_NAME}. Task ID: ${TASK_ID}. Branch: ${BRANCH_LABEL}. Convex URL: ${CONVEX_URL}. Read your SKILL.md, check your WORKING memory, query the task from Convex, and produce the '${BRANCH_LABEL}' deliverable. When done, call: npx convex run pipeline:completeBranch '{\"taskId\":\"${TASK_ID}\",\"branchLabel\":\"${BRANCH_LABEL}\",\"agentName\":\"${AGENT_NAME}\"}' --url ${CONVEX_URL} --admin-key '${ADMIN_KEY}'"
  claude -p "$PROMPT" \
    --dangerously-skip-permissions \
    --verbose \
    --output-format stream-json \
    2>"$LOG_FILE" | tee "$STREAM_FILE" >> "$LOG_FILE"

  EXIT_CODE=${PIPESTATUS[0]}

  if [ $EXIT_CODE -ne 0 ]; then
    npx convex run activities:log "{\"type\":\"error\",\"agentName\":\"${AGENT_NAME}\",\"taskId\":\"${TASK_ID}\",\"message\":\"Branch '${BRANCH_LABEL}' crashed with exit code ${EXIT_CODE}\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true
    npx convex run notifications:create "{\"mentionedAgent\":\"@human\",\"fromAgent\":\"${AGENT_NAME}\",\"taskId\":\"${TASK_ID}\",\"content\":\"Branch '${BRANCH_LABEL}' crashed (exit ${EXIT_CODE})\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true
  else
    npx convex run activities:log "{\"type\":\"complete\",\"agentName\":\"${AGENT_NAME}\",\"taskId\":\"${TASK_ID}\",\"message\":\"Branch '${BRANCH_LABEL}' completed successfully\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true
  fi

else
  # Heartbeat mode — no lock needed, agent checks for work itself
  LOG_FILE="$PROJECT_DIR/logs/${AGENT_NAME}-heartbeat-$(date +%Y%m%d-%H%M%S).log"
  cd "$PROJECT_DIR"
  PROMPT="You are ${AGENT_NAME}. Convex URL: ${CONVEX_URL}. Execute heartbeat mode — check for focus groups or tasks needing attention. Read your SKILL.md first."
  claude -p "$PROMPT" \
    --dangerously-skip-permissions \
    --verbose \
    --output-format stream-json \
    2>"$LOG_FILE" | tee -a "$LOG_FILE"

  EXIT_CODE=${PIPESTATUS[0]}

  if [ $EXIT_CODE -ne 0 ]; then
    npx convex run activities:log "{\"type\":\"error\",\"agentName\":\"${AGENT_NAME}\",\"message\":\"Heartbeat crashed with exit code ${EXIT_CODE}\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true
  fi
fi

# Post-run heartbeat
npx convex run agents:heartbeat "{\"name\":\"${AGENT_NAME}\"}" --url "$CONVEX_URL" --admin-key "$ADMIN_KEY" 2>/dev/null || true

exit $EXIT_CODE
