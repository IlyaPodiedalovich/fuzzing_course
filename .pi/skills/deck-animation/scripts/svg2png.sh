#!/usr/bin/env bash
# svg2png.sh <in.svg> <out.png> [WxH]
# Rasterize an SVG with chromium headless, at its viewBox size (default) or the given WxH.
set -e
CHROME=${CHROME:-chromium-browser}
in="$1"; out="$2"
[ -f "$in" ] || { echo "MISSING SVG: $in"; exit 1; }
dims=$(python3 -c '
import re, sys
s = open(sys.argv[1]).read()
m = re.search(r"viewBox\s*=\s*\"\s*[\d.-]+\s+[\d.-]+\s+([\d.]+)\s+([\d.]+)\"", s)
if not m: sys.exit("no viewBox in " + sys.argv[1])
print(m.group(1), m.group(2))' "$in") || exit 1
read -r W H <<< "$dims"
size="${3:-${W}x${H}}"
w="${size%%x*}"; h="${size##*x}"
"$CHROME" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --force-device-scale-factor=1 --window-size="${w},${h}" --hide-scrollbars \
  --virtual-time-budget=1500 --screenshot="$out" "file://$(realpath "$in")" 2>/dev/null
echo "wrote $out (${w}x${h})"
