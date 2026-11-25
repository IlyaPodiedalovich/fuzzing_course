#!/usr/bin/env bash
# Render a .pptx to PDF + per-slide PNGs (150 dpi) + a contact sheet.
# usage: bash render.sh <deck.pptx> <out_dir>
set -eu
DECK="$1"; OUTDIR="$2"
mkdir -p "$OUTDIR"
base=$(basename "$DECK" .pptx)
python3 "$(dirname "$0")/office/soffice.py" --headless --convert-to pdf --outdir "$OUTDIR" "$DECK" >/dev/null
pdftoppm -png -r 150 "$OUTDIR/$base.pdf" "$OUTDIR/$base"
# contact sheet: one glanceable strip (same contract as HTML decks' final-N.png)
files=$(ls "$OUTDIR"/$base-*.png | sort -V | tr '\n' ' ') # word-splitting intentional: filenames have no spaces
magick $files -resize 50% -background gray50 -splice 0x6 -append "$OUTDIR/contact-sheet.png"
ls "$OUTDIR" | grep -c png | xargs echo "png slides:"
