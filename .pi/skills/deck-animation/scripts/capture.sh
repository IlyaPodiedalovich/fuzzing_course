#!/usr/bin/env bash
# capture.sh <harness.html> <manifest.json> <outdir> [WxH]
# Figure-fragment QA capture (deck-animation):
#   - node --check on the fragment (JS syntax gate)
#   - keyframes: cold (t=0), every beat center, settled (t=1)
#   - blank-frame guard on the settled frame
#   - R3: the first informative beat center + t=1 rendered twice -> md5 must match
# Deterministic mode: ?t= pin + --virtual-time-budget (the T-8/T-9/T-10-compliant
# tween structure is the fragment author's job).
set -e
CHROME=${CHROME:-chromium-browser}
harness="$1"; man="$2"; out="$3"
[ -f "$harness" ] || { echo "MISSING HARNESS: $harness"; exit 1; }
[ -f "$man" ] || { echo "MISSING MANIFEST: $man"; exit 1; }
HDIR=$(dirname "$harness")

# window from the manifest viewBox (default if absent)
read -r W H <<< "$(python3 - "$man" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
vb = (m.get("viewBox") or "0 0 1200 900").split()
print(vb[2], vb[3])
EOF
)"
[ -n "${4:-}" ] && { W="${4%%x*}"; H="${4##*x}"; }
mkdir -p "$out"

node --check "$HDIR/fig.tl.js" && echo "js-check OK"

shot() {
  "$CHROME" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
    --force-device-scale-factor=1 --window-size=$W,$H --hide-scrollbars \
    --virtual-time-budget=$1 --screenshot="$2" "$3" 2>/dev/null
}
notblank() {
  local m
  m=$(magick "$1" -colorspace gray -format "%[fx:mean]" info: 2>/dev/null)
  if awk -v m="$m" 'BEGIN{exit !(m > 0.9)}'; then
    echo "BLANK FRAME: $1"; return 1
  fi
  return 0
}

# frames: 0.0:cold, then each beat center, then 1.0:settled
while IFS=':' read -r t name; do
  [ -z "$t" ] && continue
  shot 9000 "$out/kf-$name.png" "file://$(realpath "$harness")?t=$t"
  echo "frame kf-$name.png t=$t"
done < <(python3 - "$man" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
d = float(m["duration"])
print("0.0:cold")
for b in m["beats"]:
    tc = (float(b["t0"]) + float(b["t1"])) / 2 / d
    print(f"{tc:.4f}:{b['id']}")
print("1.0:settled")
EOF
)

notblank "$out/kf-settled.png"

# R3 double-render at the first informative beat center + t=1
R3T=$(python3 - "$man" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
d = float(m["duration"])
b = [x for x in m["beats"] if x["id"] != "b0"][0]
print(f"{(float(b['t0']) + float(b['t1'])) / 2 / d:.4f}")
EOF
)
stamp=$(basename "$out")
for t in "$R3T" "1.0"; do
  for k in 1 2; do
    shot 9000 "/tmp/r3-${stamp}-${t}-r${k}.png" "file://$(realpath "$harness")?t=$t"
  done
  m1=$(md5sum "/tmp/r3-${stamp}-${t}-r1.png" | cut -d' ' -f1)
  m2=$(md5sum "/tmp/r3-${stamp}-${t}-r2.png" | cut -d' ' -f1)
  if [ "$m1" = "$m2" ]; then echo "R3 t=$t OK"; else echo "R3 t=$t FAIL ($m1 vs $m2)"; exit 1; fi
done
echo "frames: $(ls "$out"/kf-*.png 2>/dev/null | wc -l) in $out"
