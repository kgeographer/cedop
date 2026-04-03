#!/bin/bash
# export_prospectus.sh
# --------------------
# Convert the most recent EDOP prospectus markdown to docx and pdf.
# Output goes to output/edop/docs/ for upload to Google Drive / sharing with ISHI.
#
# Usage:
#   ./scripts/export_prospectus.sh
#
# Picks the most recently dated prospectus_*.md in docs/edop/ automatically.
# Optional --file flag to target a specific file:
#   ./scripts/export_prospectus.sh --file docs/edop/prospectus_20260403.md

set -e

OUTDIR="output/edop/docs"
mkdir -p "$OUTDIR"

# Parse optional --file argument
if [[ "$1" == "--file" && -n "$2" ]]; then
    SOURCE="$2"
else
    # Auto-select most recently dated prospectus
    SOURCE=$(ls docs/edop/prospectus_*.md 2>/dev/null | sort | tail -1)
fi

if [[ -z "$SOURCE" || ! -f "$SOURCE" ]]; then
    echo "Error: no prospectus markdown found." >&2
    exit 1
fi

BASENAME=$(basename "$SOURCE" .md)

echo "Source:  $SOURCE"
echo "Output:  $OUTDIR/"

pandoc "$SOURCE" -o "$OUTDIR/${BASENAME}.docx"
echo "  wrote  ${BASENAME}.docx"

if pandoc "$SOURCE" -o "$OUTDIR/${BASENAME}.pdf" 2>/dev/null; then
    echo "  wrote  ${BASENAME}.pdf"
else
    echo "  pdf skipped (no pdf engine; export from docx in Word/Google Drive)"
fi
