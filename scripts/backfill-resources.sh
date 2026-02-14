#!/usr/bin/env bash
# Backfill resources table from existing documents + mediaAssets + reports tables.
# Idempotent via taskId+filePath upsert dedup in resources:create.
#
# Prerequisites: jq, sha256sum, npx convex
# Usage: ./scripts/backfill-resources.sh [--dry-run]

set -euo pipefail

CONVEX_URL="${CONVEX_URL:-http://localhost:3210}"
DRY_RUN=false

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "=== DRY RUN MODE ==="
fi

echo "Backfilling resources from documents + mediaAssets + reports..."
echo "Convex URL: $CONVEX_URL"
echo ""

DOCS_MIGRATED=0
MEDIA_MIGRATED=0
REPORTS_MIGRATED=0
SKIPPED=0
ERRORS=0

# ── Helper: compute content hash if file exists ──
compute_hash() {
  local filepath="$1"
  if [[ -n "$filepath" && -f "$filepath" ]]; then
    sha256sum "$filepath" | cut -d' ' -f1
  else
    echo ""
  fi
}

# ── Map document types to resource types ──
doc_type_to_resource_type() {
  case "$1" in
    deliverable)  echo "article" ;;
    research)     echo "research_material" ;;
    brief)        echo "brief" ;;
    report)       echo "report" ;;
    audience_doc) echo "research_material" ;;
    *)            echo "article" ;;
  esac
}

# ── Get all projects ──
PROJECTS=$(npx convex run projects:list '{}' --url "$CONVEX_URL" 2>/dev/null || echo "[]")
PROJECT_COUNT=$(echo "$PROJECTS" | jq 'length')
echo "Found $PROJECT_COUNT projects"
echo ""

# ══════════════════════════════════════
# 1. Migrate documents
# ══════════════════════════════════════
echo "--- Migrating documents ---"

for PROJECT_ID in $(echo "$PROJECTS" | jq -r '.[]._id // empty'); do
  PROJECT_NAME=$(echo "$PROJECTS" | jq -r --arg id "$PROJECT_ID" '.[] | select(._id == $id) | .name // "unknown"')
  DOCS=$(npx convex run documents:listByProject "{\"projectId\":\"$PROJECT_ID\"}" --url "$CONVEX_URL" 2>/dev/null || echo "[]")
  DOC_COUNT=$(echo "$DOCS" | jq 'length')

  if [[ "$DOC_COUNT" == "0" ]]; then
    continue
  fi

  echo "  Project: $PROJECT_NAME ($DOC_COUNT documents)"

  echo "$DOCS" | jq -c '.[]' | while read -r DOC; do
    DOC_ID=$(echo "$DOC" | jq -r '._id')
    TITLE=$(echo "$DOC" | jq -r '.title // "Untitled"')
    DOC_TYPE=$(echo "$DOC" | jq -r '.type // "deliverable"')
    TASK_ID=$(echo "$DOC" | jq -r '.taskId // empty')
    CAMPAIGN_ID=$(echo "$DOC" | jq -r '.campaignId // empty')
    CONTENT_BATCH_ID=$(echo "$DOC" | jq -r '.contentBatchId // empty')
    CREATED_BY=$(echo "$DOC" | jq -r '.createdBy // "backfill"')
    FILE_PATH=$(echo "$DOC" | jq -r '.filePath // empty')
    CONTENT=$(echo "$DOC" | jq -r '.content // empty')

    RESOURCE_TYPE=$(doc_type_to_resource_type "$DOC_TYPE")
    CONTENT_HASH=$(compute_hash "$FILE_PATH")

    echo "    $TITLE ($DOC_TYPE -> $RESOURCE_TYPE)"

    if [[ "$DRY_RUN" == "true" ]]; then
      continue
    fi

    # Build args JSON — only include optional fields if non-empty
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
      --arg contentHash "$CONTENT_HASH" \
      --arg docId "$DOC_ID" \
      '{
        projectId: $projectId,
        resourceType: $resourceType,
        title: $title,
        status: "draft",
        createdBy: $createdBy,
        metadata: {backfilledFrom: "documents", originalId: $docId}
      }
      + (if $taskId != "" then {taskId: $taskId} else {} end)
      + (if $campaignId != "" then {campaignId: $campaignId} else {} end)
      + (if $contentBatchId != "" then {contentBatchId: $contentBatchId} else {} end)
      + (if $filePath != "" then {filePath: $filePath} else {} end)
      + (if $contentHash != "" then {contentHash: $contentHash} else {} end)
      + (if ($content | length) > 0 then {content: $content} else {} end)
      ')

    if npx convex run resources:create "$ARGS" --url "$CONVEX_URL" >/dev/null 2>&1; then
      DOCS_MIGRATED=$((DOCS_MIGRATED + 1))
    else
      echo "      ERROR: Failed to migrate document $DOC_ID"
      ERRORS=$((ERRORS + 1))
    fi
  done
done

# ══════════════════════════════════════
# 2. Migrate mediaAssets
# ══════════════════════════════════════
echo ""
echo "--- Migrating mediaAssets ---"

for PROJECT_ID in $(echo "$PROJECTS" | jq -r '.[]._id // empty'); do
  PROJECT_NAME=$(echo "$PROJECTS" | jq -r --arg id "$PROJECT_ID" '.[] | select(._id == $id) | .name // "unknown"')
  ASSETS=$(npx convex run mediaAssets:listByProject "{\"projectId\":\"$PROJECT_ID\"}" --url "$CONVEX_URL" 2>/dev/null || echo "[]")
  ASSET_COUNT=$(echo "$ASSETS" | jq 'length')

  if [[ "$ASSET_COUNT" == "0" ]]; then
    continue
  fi

  echo "  Project: $PROJECT_NAME ($ASSET_COUNT media assets)"

  echo "$ASSETS" | jq -c '.[]' | while read -r ASSET; do
    ASSET_ID=$(echo "$ASSET" | jq -r '._id')
    ASSET_TYPE=$(echo "$ASSET" | jq -r '.type // "image"')
    PROVIDER=$(echo "$ASSET" | jq -r '.provider // "unknown"')
    PROMPT=$(echo "$ASSET" | jq -r '.promptUsed // ""')
    FILE_PATH=$(echo "$ASSET" | jq -r '.filePath // empty')
    FILE_URL=$(echo "$ASSET" | jq -r '.fileUrl // empty')
    DIMENSIONS=$(echo "$ASSET" | jq -r '.dimensions // empty')
    COST=$(echo "$ASSET" | jq -r '.generationCost // empty')
    TASK_ID=$(echo "$ASSET" | jq -r '.taskId // empty')
    CAMPAIGN_ID=$(echo "$ASSET" | jq -r '.campaignId // empty')

    # Map media type to resource type
    if [[ "$ASSET_TYPE" == "video" ]]; then
      RESOURCE_TYPE="video_script"
    else
      RESOURCE_TYPE="image"
    fi

    CONTENT_HASH=$(compute_hash "$FILE_PATH")
    TITLE="$ASSET_TYPE: $PROVIDER ($DIMENSIONS)"

    echo "    $TITLE"

    if [[ "$DRY_RUN" == "true" ]]; then
      continue
    fi

    # Get file size if file exists
    FILE_SIZE=""
    if [[ -n "$FILE_PATH" && -f "$FILE_PATH" ]]; then
      FILE_SIZE=$(stat -c%s "$FILE_PATH" 2>/dev/null || echo "")
    fi

    ARGS=$(jq -n \
      --arg projectId "$PROJECT_ID" \
      --arg resourceType "$RESOURCE_TYPE" \
      --arg title "$TITLE" \
      --arg taskId "$TASK_ID" \
      --arg campaignId "$CAMPAIGN_ID" \
      --arg filePath "$FILE_PATH" \
      --arg fileUrl "$FILE_URL" \
      --arg contentHash "$CONTENT_HASH" \
      --arg assetId "$ASSET_ID" \
      --arg provider "$PROVIDER" \
      --arg prompt "$PROMPT" \
      --arg dimensions "$DIMENSIONS" \
      --arg cost "$COST" \
      --arg fileSize "$FILE_SIZE" \
      '{
        projectId: $projectId,
        resourceType: $resourceType,
        title: $title,
        status: "draft",
        createdBy: "backfill",
        metadata: {
          backfilledFrom: "mediaAssets",
          originalId: $assetId,
          provider: $provider,
          promptUsed: $prompt,
          dimensions: $dimensions
        }
      }
      + (if $taskId != "" then {taskId: $taskId} else {} end)
      + (if $campaignId != "" then {campaignId: $campaignId} else {} end)
      + (if $filePath != "" then {filePath: $filePath} else {} end)
      + (if $fileUrl != "" then {fileUrl: $fileUrl} else {} end)
      + (if $contentHash != "" then {contentHash: $contentHash} else {} end)
      + (if $cost != "" then {metadata: {generationCost: ($cost | tonumber)}} else {} end)
      + (if $fileSize != "" then {fileSizeBytes: ($fileSize | tonumber)} else {} end)
      ')

    if npx convex run resources:create "$ARGS" --url "$CONVEX_URL" >/dev/null 2>&1; then
      MEDIA_MIGRATED=$((MEDIA_MIGRATED + 1))
    else
      echo "      ERROR: Failed to migrate media asset $ASSET_ID"
      ERRORS=$((ERRORS + 1))
    fi
  done
done

# ══════════════════════════════════════
# 3. Migrate reports
# ══════════════════════════════════════
echo ""
echo "--- Migrating reports ---"

for PROJECT_ID in $(echo "$PROJECTS" | jq -r '.[]._id // empty'); do
  PROJECT_NAME=$(echo "$PROJECTS" | jq -r --arg id "$PROJECT_ID" '.[] | select(._id == $id) | .name // "unknown"')
  REPORTS=$(npx convex run reports:listByProject "{\"projectId\":\"$PROJECT_ID\"}" --url "$CONVEX_URL" 2>/dev/null || echo "[]")
  REPORT_COUNT=$(echo "$REPORTS" | jq 'length')

  if [[ "$REPORT_COUNT" == "0" ]]; then
    continue
  fi

  echo "  Project: $PROJECT_NAME ($REPORT_COUNT reports)"

  echo "$REPORTS" | jq -c '.[]' | while read -r REPORT; do
    REPORT_ID=$(echo "$REPORT" | jq -r '._id')
    REPORT_TYPE=$(echo "$REPORT" | jq -r '.type // "report"')
    SUMMARY=$(echo "$REPORT" | jq -r '.summary // ""')
    CAMPAIGN_ID=$(echo "$REPORT" | jq -r '.campaignId // empty')
    PERIOD_START=$(echo "$REPORT" | jq -r '.periodStart // empty')
    PERIOD_END=$(echo "$REPORT" | jq -r '.periodEnd // empty')

    TITLE="Report: $REPORT_TYPE"

    echo "    $TITLE"

    if [[ "$DRY_RUN" == "true" ]]; then
      continue
    fi

    ARGS=$(jq -n \
      --arg projectId "$PROJECT_ID" \
      --arg title "$TITLE" \
      --arg campaignId "$CAMPAIGN_ID" \
      --arg summary "$SUMMARY" \
      --arg reportId "$REPORT_ID" \
      --arg reportType "$REPORT_TYPE" \
      --arg periodStart "$PERIOD_START" \
      --arg periodEnd "$PERIOD_END" \
      '{
        projectId: $projectId,
        resourceType: "report",
        title: $title,
        status: "draft",
        createdBy: "backfill",
        content: $summary,
        metadata: {
          backfilledFrom: "reports",
          originalId: $reportId,
          reportType: $reportType,
          periodStart: $periodStart,
          periodEnd: $periodEnd
        }
      }
      + (if $campaignId != "" then {campaignId: $campaignId} else {} end)
      ')

    if npx convex run resources:create "$ARGS" --url "$CONVEX_URL" >/dev/null 2>&1; then
      REPORTS_MIGRATED=$((REPORTS_MIGRATED + 1))
    else
      echo "      ERROR: Failed to migrate report $REPORT_ID"
      ERRORS=$((ERRORS + 1))
    fi
  done
done

# ══════════════════════════════════════
# Summary
# ══════════════════════════════════════
echo ""
echo "=== Backfill Complete ==="
echo "  Documents migrated: $DOCS_MIGRATED"
echo "  Media assets migrated: $MEDIA_MIGRATED"
echo "  Reports migrated: $REPORTS_MIGRATED"
echo "  Errors: $ERRORS"
echo ""
if [[ "$DRY_RUN" == "true" ]]; then
  echo "This was a dry run. No data was written."
  echo "Run without --dry-run to execute the migration."
fi
