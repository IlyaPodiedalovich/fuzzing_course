#!/usr/bin/env python3
"""fig_harness.py <fig.svg> <fig.tl.js> <manifest.json> <outdir>

Builds a self-contained capture harness for one figure fragment:
  outdir/harness.html   the figure inlined, vendored GSAP + fragment copied in,
                        ?t=<0..1> pins tl.progress() (deterministic capture), NO loop
                        (the slide loop T-14 is deck-level)
  outdir/gsap.min.js    vendored copy from this skill's scripts/lib/
  outdir/fig.tl.js      copy of the fragment
  outdir/manifest.json  copy of the manifest
"""
import pathlib
import shutil
import sys


def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    svg_p, tl_p, man_p, out_p = (pathlib.Path(a) for a in sys.argv[1:5])
    for p in (svg_p, tl_p, man_p):
        if not p.is_file():
            sys.exit(f"MISSING INPUT: {p}")
    out_p.mkdir(parents=True, exist_ok=True)

    svg = svg_p.read_text()
    shutil.copy(pathlib.Path(__file__).parent / "lib" / "gsap.min.js", out_p / "gsap.min.js")
    shutil.copy(tl_p, out_p / "fig.tl.js")
    shutil.copy(man_p, out_p / "manifest.json")

    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {{ margin: 0; padding: 0; background: #000; }}
  svg {{ display: block; margin: 0 auto; }}
</style>
</head>
<body>
{svg}
<script src="gsap.min.js"></script>
<script src="fig.tl.js"></script>
<script>
// deck-animation capture harness: pinned seek, loop-free (T-14 loop is deck-level).
(function () {{
  var tl = window.FigTl(window.gsap);
  var q = new URLSearchParams(location.search);
  if (q.has("t")) {{
    tl.progress(Math.max(0, Math.min(1, parseFloat(q.get("t")))));
  }}
  window.__figtl = tl;
  document.title = "fig " + tl.duration().toFixed(2) + "s";
}})();
</script>
</body>
</html>
"""
    (out_p / "harness.html").write_text(html)
    print(f"harness: {out_p / 'harness.html'}")


if __name__ == "__main__":
    main()
