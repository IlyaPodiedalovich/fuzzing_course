#!/usr/bin/env bash
# deck-html render + file-QA gate (ticket 11).
# usage: render_html.sh <deck.html> <outdir> [N] [MID_SLIDE]
# Produces: s<i>-t0.png, s<i>-t1.png per slide, s<MID>-mid.png, deck.pdf,
# contact-sheet.png (if montage exists), r3-a/b probe frames.
# Gates (hard, exit 1 on failure): visible-content (every settled frame
# carries pixels, F-H5), PDF page size 1440x810 pts (F-P1), pages == N,
# R3 double-capture md5-identical.
set -e
deck=$(realpath "$1"); out="$2"; N=${3:-10}; MID=${4:-1}
W=1920; H=1080
CHROME=${CHROME:-chromium-browser}
mkdir -p "$out"

shot() { # $1=budget_ms $2=outfile $3=url
  "$CHROME" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
    --force-device-scale-factor=1 --window-size=$W,$H --hide-scrollbars \
    --virtual-time-budget=$1 --screenshot="$2" "$3" 2>/dev/null
}

for i in $(seq 1 $N); do
  shot 9000 "$out/s${i}-t0.png" "file://$deck?slide=${i}&t=0"
  shot 9000 "$out/s${i}-t1.png" "file://$deck?slide=${i}&t=1"
done
shot 9000 "$out/s${MID}-mid.png" "file://$deck?slide=${MID}&t=0.5"

# F-H5 visible-content gate (ticket 03): R3 proves byte-stability of ONE
# frame — a stable background-only frame is green. Every settled capture
# must carry real content (grayscale stddev >= the threshold). Catches the
# stacked-slides bug class — mechanism and the effects-CSS rule: gotchas
# F-H5. A textured (non-solid) slide background raises the baseline — raise
# STDDEV_MIN with it if the design has one.
IM=$(command -v magick || command -v convert || true)
if [ -z "$IM" ]; then
  echo "GATE visible-content FAIL (ImageMagick 'magick'/'convert' not found)"
  exit 1
fi
STDDEV_MIN=0.01
geom_fail=0
for i in $(seq 1 $N); do
  v=$("$IM" "$out/s${i}-t1.png" -colorspace Gray \
       -format "%[fx:standard_deviation]" info: 2>/dev/null) || true
  if [ -z "$v" ] || ! awk -v v="$v" -v m="$STDDEV_MIN" 'BEGIN{exit !(v+0 >= m+0)}'; then
    echo "GATE visible-content FAIL (slide $i: stddev ${v:-?} < $STDDEV_MIN — no visible content)"
    geom_fail=1
  fi
done
if [ "$geom_fail" -ne 0 ]; then exit 1; fi
echo "GATE visible-content PASS ($N settled frames carry content)"

# R3 probe: two identical captures must be byte-identical
shot 9000 "$out/r3-a.png" "file://$deck?slide=1&t=1"
shot 9000 "$out/r3-b.png" "file://$deck?slide=1&t=1"

"$CHROME" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --force-device-scale-factor=1 --window-size=$W,$H \
  --no-pdf-header-footer --virtual-time-budget=9000 \
  --print-to-pdf="$out/deck.pdf" "file://$deck" 2>/dev/null

psize=$(pdfinfo "$out/deck.pdf" | awk '/Page size/{print $3" x "$5" "$6}')
pages=$(pdfinfo "$out/deck.pdf" | awk '/Pages/{print $2}')

ra=$(md5sum "$out/r3-a.png" | cut -d' ' -f1)
rb=$(md5sum "$out/r3-b.png" | cut -d' ' -f1)

[ "$psize" = "1440 x 810 pts" ] \
  && echo "GATE pdf-size PASS ($psize)" \
  || { echo "GATE pdf-size FAIL ($psize)"; exit 1; }
[ "$pages" = "$N" ] \
  && echo "GATE pdf-pages PASS ($pages)" \
  || { echo "GATE pdf-pages FAIL ($pages != $N)"; exit 1; }
[ "$ra" = "$rb" ] \
  && echo "GATE r3 PASS ($ra)" \
  || { echo "GATE r3 FAIL ($ra != $rb)"; exit 1; }

if command -v montage >/dev/null 2>&1; then
  montage "$out"/s*-t1.png -tile 3x -geometry +4+4 -background black \
    "$out/contact-sheet.png" 2>/dev/null || true
fi
cp "$out/deck.pdf" "$(dirname "$deck")/deck.pdf" 2>/dev/null || true
echo "done: $N slides, pdf $pages pages, mid=s${MID}"
