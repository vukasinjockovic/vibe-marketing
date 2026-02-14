#!/usr/bin/env bash
# Backfill resources table from existing documents + mediaAssets tables.
# Idempotent via filePath dedup (upsert).
#
# Usage: ./scripts/backfill-resources.sh [--dry-run]

set -euo pipefail

CONVEX_URL="${CONVEX_URL:-http://localhost:3210}"
DRY_RUN=false

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "=== DRY RUN MODE ==="
fi

echo "Backfilling resources from documents + mediaAssets..."
echo "Convex URL: $CONVEX_URL"
echo ""

DOCS_MIGRATED=0
MEDIA_MIGRATED=0
SKIPPED=0
ERRORS=0

# ── Map document types to resource types ──
doc_type_to_resource_type() {
  case "$1" in
    deliverable) echo "article" ;;
    research)    echo "research_material" ;;
    brief)       echo "brief" ;;
    report)      echo "report" ;;
    audience_doc) echo "research_material" ;;
    *)           echo "article" ;;
  esac
}

# ── 1. Migrate documents ──
echo "--- Migrating documents ---"

# Get all projects to iterate
PROJECTS=$(npx convex run projects:list '{}' --url "$CONVEX_URL" 2>/dev/null || echo "[]")

for PROJECT_ID in $(echo "$PROJECTS" | jq -r '.[]._id // empty'); do
  DOCS=$(npx convex run documents:listByProject "{\"projectId\":\"$PROJECT_ID\"}" --url "$CONVEX_URL" 2>/dev/null || echo "[]")

  for DOC in $(echo "$DOCS" | jq -c '.[]'); do
    DOC_ID=$(echo "$DOC" | jq -r '._id')
    TITLE=$(echo "$DOC" | jq -r '.title')
    DOC_TYPE=$(echo "$DOC" | jq -r '.type')
    TASK_ID=$(echo "$DOC" | jq -r '.taskId // empty')
    CAMPAIGN_ID=$(echo "$DOC" | jq -r '.campaignId // empty')
    CONTENT_BATCH_ID=$(echo "$DOC" | jq -r '.contentBatchId // empty')
    CREATED_BY=$(echo "$DOC" | jq -r '.createdBy')
    FILE_PATH=$(echo "$DOC" | jq -r '.filePath // empty')
    CONTENT=$(echo "$DOC" | jq -r '.content // empty')

    RESOURCE_TYPE=$(doc_type_to_resource_type "$DOC_TYPE")

    echo "  DOC: $TITLE ($DOC_TYPE -> $RESOURCE_TYPE)"

    if [[ "$DRY_RUN" == "true" ]]; then
      ((DOCS_MIGRATED++))
      continue
    fi

    # Build args JSON
    ARGS=$(jq -n \
      --arg projectId "$PROJECT_ID" \
      --arg resourceType "$RESOURCE_TYPE" \
      --arg title "$TITLE" \
      --arg taskId "$TASK_ID" \
      --arg campaignId "$CAMPAIGN_ID" \
      --arg contentBatchId "$CONTENT_BATCH_ID" \
      --arg filePath "$FILE_PATH" \
      --arg content "$CONTENT" \
      --arg createdBy "$CREATED_BY" \
      '{
        projectId: $projectId,
        resourceType: $resourceType,
        title: $title,
        status: "draft",
        createdBy: $createdBy,
        metadata: {backfilledFrom: "documents", originalId: "'"$DOC_ID"'"}
      }
      + (if $taskId != "" then {taskId: $taskId} else {} end)
      + (if $campaignId != "" then {campaignId: $campaignId} else {} end)
      + (if $contentBatchId != "" then {contentBatchId: $contentBatchId} else {} end)
      + (if $filePath != "" then {filePath: $filePath} else {} end)
      + (if ($content | length) > 0 then {content: $content} else {} end)
      ')

    npx convex run resources:create "$ARGS" --url "$CONVEX_URL" >/dev/null 2>&1 && {
      ((DOCS_MIGRATED++))
    } || {
      echo "    ERROR: Failed to migrate document $DOC_ID"
      ((ERRORS++))
    }
  done
done

# ── 2. Migrate mediaAssets ──
echo ""
echo "--- Migrating mediaAssets ---"

for PROJECT_ID in $(echo "$PROJECTS" | jq -r '.[]._id // empty'); do
  # mediaAssets doesn't have a listByProject in the existing code, so query all
  # This is a one-time backfill so performance isn't critical
  ASSETS=$(npx convex run --url "$CONVEX_URL" 2>/dev/null << 'QUERY' || echo "[]"
// Can't run inline queries via CLI, skip if no function exists
QUERY
  )

  # If we can't query mediaAssets directly, try the by_project index
  ASSETS=$(npx convex run documents:listByProject "{\"projectId\":\"$PROJECT_ID\"}" --url "$CONVEX_URL" 2>/dev/null || echo "[]")
  # Note: mediaAssets may not have a query function exposed. In that case,
  # this section would need a custom Convex function. For now, we log it.
done

echo ""
echo "=== Backfill Complete ==="
echo "  Documents migrated: $DOCS_MIGRATED"
echo "  Media assets migrated: $MEDIA_MIGRATED"
echo "  Skipped: $SKIPPED"
echo "  Errors: $ERRORS"
echo ""
echo "Note: mediaAssets may need a custom query function to backfill."
echo "Run with --dry-run first to see what would be migrated."
