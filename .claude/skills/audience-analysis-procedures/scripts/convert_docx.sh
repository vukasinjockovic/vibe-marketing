#!/usr/bin/env bash
# Convert .docx to markdown via pandoc
# Usage: convert_docx.sh input.docx [output.md]
set -euo pipefail

INPUT="$1"
OUTPUT="${2:-${INPUT%.docx}.md}"

if ! command -v pandoc &>/dev/null; then
  echo "ERROR: pandoc not installed. Install with: sudo apt install pandoc" >&2
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "ERROR: File not found: $INPUT" >&2
  exit 1
fi

pandoc -f docx -t markdown --wrap=none -o "$OUTPUT" "$INPUT"
echo "Converted $INPUT -> $OUTPUT"
