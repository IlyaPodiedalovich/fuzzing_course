#!/usr/bin/env python3
"""deck-html assembler (per-slide authoring route, ticket 01).

Builds the TRUE single-file deck.html from per-slide hand-authored slide files.
Layer split: this script owns layer 1 (the machine — vendor stage CSS, print
contract, capture rules, tokens :root, GSAP inlining, FIGS map, runtime).
The author owns layer 2 (the slide markup and the theme/design-system CSS).

Slide file contract (one .html file per slide, named NN-<id>.html so the
sorted order is the deck order):
  - exactly one <section> per file, well-formed for content_check G-1:
      <section class="slide <layout-word> [extra...]" id="<skeleton-id>">
  - the section id must equal the skeleton slide id (content_check keys on it);
  - optional figure: one <!--FIG:<fid>--> marker, where <fid> MUST equal the
    section id (the runtime looks up window.FIGS by section id). Assets:
    <figs>/fig-<fid>.svg (inlined at the marker) and <figs>/fig-<fid>.tl.js
    (the fragment: `window.FigTl = (gsap) => { ... };`).

usage:
  assemble.py <slides-dir> <out.html> --tokens <tokens.json> --styles <theme.css>
             [--effects <effects.css>] [--figs <assets-dir>]
             [--skeleton <skeleton.yaml|json>] [--runtime <runtime.js>]

--skeleton makes the assembler enforce: slide ids and file order match the
skeleton. --runtime defaults to the loop-free variant (slide activation is the
only animation trigger); pass scripts/runtime.js for T-14 deck-level loops.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

from deck_common import (SECTION_RE, token_css, font_faces,
                         load_skeleton, load_theme)  # noqa: E402
VIEWPORT_CSS = open(os.path.join(HERE, "lib", "viewport-base.css"), encoding="utf-8").read()
GSAP_JS = open(os.path.join(HERE, "lib", "gsap.min.js"), encoding="utf-8").read()
DEFAULT_RUNTIME = os.path.join(HERE, "runtime-noloop.js")

# Layer 1 (machine) CSS — emitted by the assembler, never hand-written:
# box model, the F-P1 @page rule, the F-P2 print contract (settled state by
# CSS, not runtime state), the t-pinned capture rules (F-H4/C-4: no CSS
# transitions on slide visibility; fit-to-window off in captures), and the
# token-driven .slide base.
MACHINE_CSS = """
*{box-sizing:border-box} figure{margin:0}
/* F-P1: print pages exactly one slide (Letter pages clip the 1920px slide) */
@page{size:1920px 1080px;margin:0}
/* F-P2: settled text state guaranteed by CSS, not runtime state */
@media print{
  .reveal{opacity:1!important;transform:none!important}
  .flow-el{display:none!important}
}
html.t-pinned .slide{transition:none!important}
html.t-pinned .deck-stage{transform:none!important}
.slide{font-family:var(--font);color:var(--body);background:var(--slide-bg)}
"""


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def figs_entry(fid, figs_dir):
    svg_path = os.path.join(figs_dir, f"fig-{fid}.svg")
    tl_path = os.path.join(figs_dir, f"fig-{fid}.tl.js")
    if not os.path.exists(svg_path):
        sys.exit(f"figure '{fid}': {svg_path} not found")
    svg = rd(svg_path)
    if not os.path.exists(tl_path):
        print(f"WARN: {tl_path} not found — figure '{fid}' is static (no fragment)",
              file=sys.stderr)
        return svg, None
    body = rd(tl_path)
    header = "window.FigTl = (gsap) => {"
    if header not in body:
        sys.exit(f"{tl_path}: expected header `{header}` — the FIGS embedding "
                 f"strips exactly that header; fix the fragment file")
    body = body.replace(header, "", 1).strip()
    # the standalone fragment file ends with `};` — strip it: a dangling `;`
    # between FIGS entries is a SyntaxError that kills the whole script block.
    if body.endswith("};"):
        body = body[:-2]
    elif body.endswith("}"):
        body = body[:-1]
    return svg, f'  "{fid}": (gsap) => {{\n{body}\n  }},'


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slides_dir")
    ap.add_argument("out")
    ap.add_argument("--tokens", required=True)
    ap.add_argument("--styles", required=True,
                    help="layer-2 CSS: the design system / component kit + per-slide layout")
    ap.add_argument("--effects", default=None, help="optional factura/effects.css layer")
    ap.add_argument("--figs", default=None, help="assets dir with fig-<fid>.{svg,tl.js}")
    ap.add_argument("--skeleton", default=None,
                    help="enforce slide ids + file order against the skeleton")
    ap.add_argument("--runtime", default=DEFAULT_RUNTIME,
                    help=f"runtime JS (default: {os.path.basename(DEFAULT_RUNTIME)}, loop-free)")
    a = ap.parse_args()

    files = sorted(f for f in os.listdir(a.slides_dir) if f.endswith(".html"))
    if not files:
        sys.exit(f"no .html slide files in {a.slides_dir}")

    slides, figs_js, ids, fig_el_ids = [], [], [], {}
    for f in files:
        h = rd(os.path.join(a.slides_dir, f))
        sec = re.search(r"<section\b[^>]*>", h)
        if not sec or not SECTION_RE.fullmatch(sec.group(0)):
            sys.exit(f"{f}: no well-formed <section class=\"slide ...\" id=\"...\"> (G-1)")
        m = re.search(r'id="([^"]+)"', sec.group(0))
        sid = m.group(1)
        if sid in ids:
            sys.exit(f"duplicate slide id '{sid}' ({f})")
        ids.append(sid)
        markers = re.findall(r"<!--FIG:(\w+)-->", h)
        if len(markers) > 1:
            sys.exit(f"{f}: {len(markers)} FIG markers — the runtime supports one figure per slide")
        if markers and a.figs:
            fid = markers[0]
            if fid != sid:
                sys.exit(f"{f}: FIG marker '{fid}' mismatches section id '{sid}' — "
                         f"the runtime looks up window.FIGS by section id")
            svg, entry = figs_entry(fid, a.figs)
            for el_id in re.findall(r'\bid="([^"]+)"', svg):
                if el_id in fig_el_ids:
                    sys.exit(f"duplicate figure element id '{el_id}' "
                             f"(figures '{fig_el_ids[el_id]}' and '{fid}') — "
                             f"figure element ids are SLIDE-SCOPED: prefix them "
                             f"with the figure's slide key (deck-animation "
                             f"SKILL.md step 2; gotchas K-5)")
                fig_el_ids[el_id] = fid
            h = h.replace(f"<!--FIG:{fid}-->", svg)
            if entry:
                figs_js.append(entry)
        elif markers and not a.figs:
            sys.exit(f"{f}: FIG marker '{markers[0]}' but --figs was not given")
        if "<!--FIG:" in h:
            sys.exit(f"{f}: unhandled FIG marker left in the slide")
        slides.append(h)

    sk = load_skeleton(a.skeleton) if a.skeleton else None
    if sk:
        sk_ids = [s.get("id") for s in sk.get("slides", [])]
        if sk_ids != ids:
            sys.exit(f"slide file order/ids {ids} do not match skeleton order {sk_ids}")

    n = len(slides)
    effects = rd(a.effects) if a.effects else ""
    theme = load_theme(a.tokens)
    meta = (sk or {}).get("meta", {}) if sk else {}
    title = meta.get("title", "deck")
    lang = meta.get("lang", "ru")
    html = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
{VIEWPORT_CSS}
{MACHINE_CSS}
{token_css(theme)}
{font_faces(theme, os.path.dirname(os.path.abspath(a.tokens)))}
{rd(a.styles)}
{effects}
</style>
</head>
<body>
<div class="deck-viewport"><div class="deck-stage">
{''.join(slides)}
</div></div>
<script>/* GSAP (vendored) */
{GSAP_JS}
</script>
<script>
window.__N__ = {n};
window.FIGS = {{
{chr(10).join(figs_js)}
}};
</script>
<script>/* deck runtime */
{rd(a.runtime)}
</script>
</body>
</html>
"""
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {a.out} ({len(html)} bytes, {n} slides, {len(figs_js)} figures)")


if __name__ == "__main__":
    main()
