#!/usr/bin/env bash
# Compute SHA-256 hash of a file's content.
# Usage: ./scripts/compute-content-hash.sh <file-path>
# Output: hash string (64 hex chars)

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <file-path>" >&2
  exit 1
fi

FILE="$1"

if [[ ! -f "$FILE" ]]; then
  echo "ERROR: File not found: $FILE" >&2
  exit 1
fi

sha256sum "$FILE" | cut -d' ' -f1
