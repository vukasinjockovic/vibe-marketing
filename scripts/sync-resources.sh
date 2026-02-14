#!/usr/bin/env bash
# Sync resources table with filesystem.
# - Updates content hash if file changed
# - Flags resources as orphaned if file missing
#
# Usage: ./scripts/sync-resources.sh [--dry-run]

set -euo pipefail

CONVEX_URL="${CONVEX_URL:-http://localhost:3210}"
DRY_RUN=false

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "=== DRY RUN MODE ==="
fi

echo "Syncing resources from filesystem..."
echo "Convex URL: $CONVEX_URL"
echo ""

# Get all resources with filePath set
RESOURCES=$(npx convex run resources:listByProject '{"projectId":"PLACEHOLDER"}' --url "$CONVEX_URL" 2>/dev/null || echo "[]")

# Since we can't easily iterate all projects via CLI, use a simpler approach:
# Query all resources that have a filePath by scanning projects
PROJECTS=$(npx convex run projects:list '{}' --url "$CONVEX_URL" 2>/dev/null || echo "[]")

SYNCED=0
ORPHANED=0
UNCHANGED=0
ERRORS=0

# Process each project's resources
for PROJECT_ID in $(echo "$PROJECTS" | jq -r '.[]._id // empty'); do
  RESOURCES=$(npx convex run resources:listByProject "{\"projectId\":\"$PROJECT_ID\"}" --url "$CONVEX_URL" 2>/dev/null || echo '{"page":[]}')

  for ROW in $(echo "$RESOURCES" | jq -c '.page[] | select(.filePath != null)'); do
    RESOURCE_ID=$(echo "$ROW" | jq -r '._id')
    FILE_PATH=$(echo "$ROW" | jq -r '.filePath')
    OLD_HASH=$(echo "$ROW" | jq -r '.contentHash // ""')
    TITLE=$(echo "$ROW" | jq -r '.title')

    if [[ ! -f "$FILE_PATH" ]]; then
      echo "  ORPHAN: $TITLE ($FILE_PATH)"
      if [[ "$DRY_RUN" == "false" ]]; then
        npx convex run resources:update "{\"id\":\"$RESOURCE_ID\",\"fileOrphaned\":true,\"updatedBy\":\"sync-script\"}" --url "$CONVEX_URL" >/dev/null 2>&1 || true
      fi
      ((ORPHANED++))
      continue
    fi

    NEW_HASH=$(sha256sum "$FILE_PATH" | cut -d' ' -f1)

    if [[ "$NEW_HASH" == "$OLD_HASH" ]]; then
      ((UNCHANGED++))
      continue
    fi

    echo "  SYNC: $TITLE (hash changed)"
    if [[ "$DRY_RUN" == "false" ]]; then
      FILE_SIZE=$(stat -c%s "$FILE_PATH" 2>/dev/null || stat -f%z "$FILE_PATH" 2>/dev/null || echo "0")
      # Read file content for text files
      MIME=$(file --mime-type -b "$FILE_PATH" 2>/dev/null || echo "application/octet-stream")
      if [[ "$MIME" == text/* ]]; then
        CONTENT=$(jq -Rs . < "$FILE_PATH")
        npx convex run resources:syncFromFile "{\"id\":\"$RESOURCE_ID\",\"contentHash\":\"$NEW_HASH\",\"content\":$CONTENT,\"fileSizeBytes\":$FILE_SIZE,\"syncedBy\":\"sync-script\"}" --url "$CONVEX_URL" >/dev/null 2>&1 || {
          echo "    ERROR: Failed to sync $RESOURCE_ID"
          ((ERRORS++))
          continue
        }
      else
        npx convex run resources:syncFromFile "{\"id\":\"$RESOURCE_ID\",\"contentHash\":\"$NEW_HASH\",\"fileSizeBytes\":$FILE_SIZE,\"syncedBy\":\"sync-script\"}" --url "$CONVEX_URL" >/dev/null 2>&1 || {
          echo "    ERROR: Failed to sync $RESOURCE_ID"
          ((ERRORS++))
          continue
        }
      fi
    fi
    ((SYNCED++))
  done
done

echo ""
echo "=== Sync Complete ==="
echo "  Synced:    $SYNCED"
echo "  Unchanged: $UNCHANGED"
echo "  Orphaned:  $ORPHANED"
echo "  Errors:    $ERRORS"
