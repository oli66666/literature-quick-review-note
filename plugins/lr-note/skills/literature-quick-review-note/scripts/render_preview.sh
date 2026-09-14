#!/usr/bin/env bash
# render_preview.sh
#
# Renders a .docx to PDF and then to one JPEG per page, so you can actually
# look at the result (table colors, heading hierarchy, layout) before
# delivering it — validation passing is not the same as looking right.
#
# Requires: LibreOffice (the `soffice` binary) and poppler-utils (`pdftoppm`).
#   Debian/Ubuntu: apt-get install libreoffice poppler-utils
#   macOS (Homebrew): brew install --cask libreoffice && brew install poppler
#
# Usage:
#   bash render_preview.sh mynote.docx [output_dir] [--comments]
#
# The `bash` prefix avoids depending on this file's executable bit, which does
# not always survive a clone or a zip round-trip. If you would rather run it as
# ./render_preview.sh, record the bit once with:
#   git update-index --chmod=+x scripts/render_preview.sh
#
# --comments  also renders Word margin comments into the PDF margin, so you can
#             see where each comment actually landed. Use this after running
#             insert_comments.py; without it the comments exist in the file but
#             are invisible in the preview.
#
# Produces <output_dir>/mynote.pdf and <output_dir>/mynote-pg-1.jpg, -2.jpg, ...

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <file.docx> [output_dir] [--comments]" >&2
  exit 1
fi

INPUT=""
OUTDIR=""
SHOW_COMMENTS=0

for arg in "$@"; do
  case "$arg" in
    --comments) SHOW_COMMENTS=1 ;;
    *)
      if [ -z "$INPUT" ]; then INPUT="$arg"
      elif [ -z "$OUTDIR" ]; then OUTDIR="$arg"
      fi
      ;;
  esac
done

if [ -z "$INPUT" ]; then
  echo "Usage: $0 <file.docx> [output_dir] [--comments]" >&2
  exit 1
fi

OUTDIR="${OUTDIR:-$(dirname "$INPUT")}"
BASENAME="$(basename "${INPUT%.*}")"

FILTER="pdf"
if [ "$SHOW_COMMENTS" -eq 1 ]; then
  FILTER='pdf:writer_pdf_Export:{"ExportNotesInMargin":{"type":"boolean","value":"true"}}'
fi

mkdir -p "$OUTDIR"
soffice --headless --convert-to "$FILTER" --outdir "$OUTDIR" "$INPUT"
pdftoppm -jpeg -r 100 "$OUTDIR/$BASENAME.pdf" "$OUTDIR/$BASENAME-pg"

echo "Rendered: $OUTDIR/$BASENAME.pdf and $OUTDIR/$BASENAME-pg-*.jpg"
if [ "$SHOW_COMMENTS" -eq 1 ]; then
  echo "(margin comments included; pdftoppm may warn 'Bad bounding box for annotation' — harmless)"
fi
