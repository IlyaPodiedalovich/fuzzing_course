#!/usr/bin/env python3
"""deck-html generator (ticket 11).

skeleton (YAML/JSON, schema v1.1) + theme tokens (+ effects.css, + figure assets
from the deck-animation skill) -> TRUE single-file deck.html: all CSS inlined,
GSAP inlined, settled figure SVGs + fragments inlined, font subsets base64-embedded.
Print contract: @page 1920x1080, settled state guaranteed by CSS + authored SVG base.

usage:
  gen_deck.py <skeleton.yaml|json> --theme <tokens.json>
             [--effects <effects.css>] [--figs <assets-dir>]
             [--loop] <out.html>

The runtime defaults to the loop-free variant (slide activation is the only
animation trigger — the loop policy); --loop selects the T-14 loop-capable
runtime for a deck whose user-stated policy wants figure replays.

Figure assets (per slide id): assets/fig-<id>.svg (+ fig-<id>.tl.js). Without
--figs the generator emits placeholder figure panels (dev mode) and warns.
"""
import sys
import os
import re
import json
import math
import html as _html
import base64

try:
    import yaml
except ImportError:
    yaml = None

HERE = os.path.dirname(os.path.abspath(__file__))
VIEWPORT_CSS = open(os.path.join(HERE, "lib", "viewport-base.css"), encoding="utf-8").read()
RUNTIME_NOLOOP_JS = open(os.path.join(HERE, "runtime-noloop.js"),
                         encoding="utf-8").read()
RUNTIME_LOOP_JS = open(os.path.join(HERE, "runtime.js"), encoding="utf-8").read()
GSAP_JS = open(os.path.join(HERE, "lib", "gsap.min.js"), encoding="utf-8").read()

def esc(s):
    return _html.escape(s if s is not None else "", quote=False)


def norm_lines(text):
    return [l.strip() for l in (text or "").splitlines() if l.strip()]


def est_title_lines(title, layout):
    cpl = {"content-left": 33, "content-right": 33, "full": 61, "table": 61,
           "diagram": 61, "cards": 61, "grid-5": 61}.get(layout, 33)
    return max(1, math.ceil(len(title or "") / cpl))


# shared helpers live in deck_common.py (single source for the generator,
# the assembler and the content gate — see that module)
from deck_common import (SECTION_RE, LATIN_RANGE, CYR_RANGE, load_skeleton,
                         load_theme, token_css, font_faces)  # noqa: E402


CONTENT_CSS = """
/* F-P1: print pages exactly one slide (Letter pages clip the 1920px slide) */
@page{size:1920px 1080px;margin:0}
/* Print contract (F-P2): settled text state guaranteed by CSS, not runtime state */
@media print{
  .reveal{opacity:1!important;transform:none!important}
  .flow-el{display:none!important}
}
*{box-sizing:border-box} figure{margin:0}
.slide{font-family:var(--font);color:var(--body);background:var(--slide-bg)}
/* NOTE: no CSS transition on .slide — headless chromium --virtual-time-budget
   captures stall CSS transitions at 0 (slide stays invisible); slide reveal is
   instant, all motion is GSAP (seekable + capture-safe). See gotchas.md. */
html.t-pinned .slide{transition:none!important}
html.t-pinned .deck-stage{transform:none!important}
.slide .inner{position:absolute;inset:0;padding:var(--pad)}
.s-title{margin:0 0 40px;font-size:56px;font-weight:700;color:var(--title);line-height:1.15}
/* title width per layout + two-line titles shift the zones down (never overlap the figure) */
.slide.layout-content-left .s-title{max-width:1032px}
.slide.layout-content-right .s-title{width:1032px;margin-left:744px}
.slide.layout-full .s-title,.slide.layout-table .s-title{max-width:1776px}
.slide.title-2 .s-title{margin-bottom:20px}
.slide.title-2 .content{top:250px}
.slide.title-2 .figure{top:250px}
.slide.title-2 .cards{top:250px}
.slide.title-2.layout-full.has-fig .content{height:270px}
.slide.title-2.layout-full .figure-bottom{top:470px}
.slide.title-2.layout-diagram .content{height:100px}
.slide.title-2.layout-diagram .figure-bottom{top:450px}
/* layout zones (1920x1080 authored space — see references/layout-constants.md) */
.content{position:absolute;top:165px;left:var(--pad);bottom:var(--pad);width:1032px}
.slide.layout-content-right .content{left:816px}
.slide.layout-content-right .figure{left:var(--pad);right:auto}
.slide.layout-full .content{width:1776px}
.slide.layout-table .content{width:1776px}
.slide.layout-full.has-fig .content{bottom:auto;height:360px;overflow:hidden}
.slide.layout-diagram .content{width:1776px;bottom:auto;height:190px;overflow:hidden}
.slide.layout-diagram .figure-bottom{top:390px}
.cards{position:absolute;top:165px;left:var(--pad);right:var(--pad);bottom:var(--pad);
       display:grid;gap:24px}
.slide.layout-cards .cards{grid-template-columns:repeat(2,1fr)}
.slide.layout-grid-5 .cards{grid-template-columns:repeat(5,1fr)}
.card{background:var(--figfill);border:1px solid var(--figline);border-radius:12px;padding:22px}
.card .c-title{font-size:28px;font-weight:700;color:var(--title);margin-bottom:10px}
.card .c-body{font-size:25px;line-height:1.4}
/* blocks */
ul.b{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:18px}
ul.b li{position:relative;padding-left:34px;font-size:25px;line-height:1.42}
ul.b li::before{content:"";position:absolute;left:0;top:12px;width:14px;height:14px;
               background:var(--accent)}
ul.b li.sub{padding-left:68px}
ul.b li.sub::before{left:34px;top:14px;width:8px;height:8px}
p.txt{font-size:25px;line-height:1.45;margin:0 0 18px}
.formula{font-size:30px;font-weight:700;color:var(--title);margin:22px 0;padding:18px 22px;
         background:var(--figfill);border-left:4px solid var(--accent);border-radius:8px;
         white-space:pre-wrap}
/* one line per element: multi-line typed blocks (.ln spans/ps) must not glue
   into one inline line (the whitespace contract, layout-constants.md) */
.ln{display:block;min-height:1.2em}
.f-cap{font-size:18px;color:var(--figtext);font-weight:400;margin-top:8px}
/* tables: explicit fills (dark-theme discipline) */
table.tbl{width:100%;border-collapse:collapse;font-size:18px}
.tbl th{background:var(--accent);color:var(--headertext);text-align:left;
        padding:10px 14px;font-size:18px}
.tbl td{padding:9px 14px;border-bottom:1px solid var(--figline);background:var(--slide-bg)}
.tbl tbody tr:nth-child(even) td{background:var(--rowalt)}
/* figures */
.figure{position:absolute;top:165px;right:var(--pad);width:720px;height:843px;
        background:var(--figfill);border:2px solid var(--figline);border-radius:16px;
        padding:24px;display:flex;flex-direction:column;gap:12px}
.figure .fig-svg{flex:1;min-height:0}
.figure .fig-svg svg{width:100%;height:100%;display:block}
.figure figcaption,.figure-bottom figcaption,.diagram-zone figcaption{
        font-size:20px;color:var(--figtext)}
.fig-prompt{font-size:22px;color:var(--figtext);font-style:italic;flex:1}
.figure-bottom{position:absolute;top:560px;left:var(--pad);right:var(--pad);bottom:var(--pad);
        background:var(--figfill);border:2px solid var(--figline);border-radius:16px;
        padding:24px;display:flex;flex-direction:column;gap:12px}
.figure-bottom .fig-svg{flex:1;min-height:0}
.figure-bottom .fig-svg svg{width:100%;height:100%;display:block}
.diagram-zone{position:absolute;top:165px;left:var(--pad);right:var(--pad);bottom:140px;
        background:var(--figfill);border:2px solid var(--figline);border-radius:16px;
        padding:24px;display:flex;flex-direction:column;gap:12px}
.diagram-zone .fig-svg{flex:1;min-height:0}
.diagram-zone .fig-svg svg{width:100%;height:100%;display:block}
svg{font-family:inherit}
/* section (title) layout */
.slide.layout-section .inner{display:flex;flex-direction:column;justify-content:center}
.slide.layout-section .sec-kicker{font-size:26px;font-weight:700;letter-spacing:.22em;
        text-transform:uppercase;color:var(--accent)}
.slide.layout-section h1.s-title{font-size:92px;line-height:1.08;margin:36px 0 0;
        max-width:1560px}
.slide.layout-section .sec-sub{font-size:34px;line-height:1.5;margin-top:36px;
        max-width:1280px}
.slide.layout-section .sec-rule{width:180px;height:6px;background:var(--accent);margin-top:48px}
.pageno{position:absolute;right:48px;bottom:32px;font-size:18px;color:var(--figtext)}
"""


def read_figure(slide, figs_dir):
    """-> dict(svg|None, prompt|None, caption|None, frag|None, loop:bool)"""
    fig = slide.get("figure") or {}
    fid = slide["id"]
    out = {"svg": None, "prompt": fig.get("prompt"), "caption": fig.get("caption"),
           "frag": None, "loop": False}
    if figs_dir:
        p = os.path.join(figs_dir, f"fig-{fid}.svg")
        if os.path.exists(p):
            svg = open(p, encoding="utf-8").read()
            svg = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", svg, flags=re.S)
            out["svg"] = svg
            fp = os.path.join(figs_dir, f"fig-{fid}.tl.js")
            if os.path.exists(fp):
                out["frag"] = open(fp, encoding="utf-8").read()
                out["loop"] = fig.get("loop", True)  # skeleton figure may set loop: false
            else:
                print(f"WARN: {p} without {fp} — static figure (no loop)", file=sys.stderr)
        else:
            print(f"WARN: no {p} — placeholder figure panel", file=sys.stderr)
    else:
        if fig:
            print(f"WARN: --figs not given — placeholder figure for {fid}", file=sys.stderr)
    return out


def figure_zone_html(f, zone="figure"):
    cap = f'<figcaption>{esc(f["caption"])}</figcaption>' if f.get("caption") else ""
    if f["svg"]:
        return (f'<figure class="{zone}"><div class="fig-svg">{f["svg"]}</div>{cap}</figure>')
    prompt = f'<div class="fig-prompt">{esc(f.get("prompt") or "")}</div>'
    label = '<div class="fig-label" style="font-size:18px;font-weight:700;letter-spacing:.14em;color:var(--figtext)">FIG</div>'
    return f'<figure class="{zone}">{label}{prompt}{cap}</figure>'


def blocks_html(blocks):
    parts = []
    for b in blocks:
        t = b["type"]
        # optional skeleton field `beat: bN` groups .reveal items into
        # per-beat waves (runtime.js); without it everything is one wave
        rb = f' data-beat="{b["beat"]}"' if b.get("beat") else ""
        rf = f' data-fx="{b["fx"]}"' if b.get("fx") else ""
        is_mask = b.get("fx") == "mask"
        is_type = b.get("fx") == "type"
        if t == "bullet":
            lis = ""
            for raw in (b.get("text") or "").splitlines():
                l = raw.strip()
                if not l:
                    continue
                # an indented line (exactly two leading spaces) is a sub-item
                # (level 2, .sub); any other indent is undefined -> level 1
                cls = "reveal sub" if raw[:2] == "  " and raw[2:3] != " " else "reveal"
                lis += f'<li class="{cls}"{rb}{rf}>{esc(l)}</li>'
            parts.append(f'<ul class="b">{lis}</ul>')
        elif t == "text":
            if is_type:
                # per-line console typing: each source line is its own .reveal
                # (same beat -> the runtime stagger prints them line by line)
                lines = "".join(
                    f'<p class="txt ln reveal"{rb}{rf}>{esc(l) or "&nbsp;"}</p>'
                    for l in norm_lines(b.get("text")))
                parts.append(lines)
            else:
                inner = f'<p class="txt reveal"{rb}{rf}>{esc(b.get("text"))}</p>'
                if is_mask:
                    inner = f'<span class="fxwipe">{inner}</span>'
                parts.append(inner)
        elif t == "formula":
            cap = (f'<div class="f-cap reveal"{rb}{rf}>{esc(b["caption"])}</div>'
                   if b.get("caption") else "")
            if is_type:
                lines = b.get("text", "").split("\n")
                if lines and lines[-1] == "":
                    lines = lines[:-1]
                body = "".join(
                    f'<span class="ln reveal"{rb}{rf}>{esc(l) or "&nbsp;"}</span>'
                    for l in lines)
                parts.append(f'<div class="formula">{body}{cap}</div>')
            else:
                inner = (f'<div class="formula reveal"{rb}{rf}>'
                         f'{esc(b.get("text"))}{cap}</div>')
                if is_mask:
                    inner = f'<span class="fxwipe">{inner}</span>'
                parts.append(inner)
        elif t == "table":
            thead = "".join(f"<th>{esc(c)}</th>" for c in b.get("columns", []))
            rows = "".join(
                "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>"
                for r in b.get("rows", []))
            inner = (f'<table class="tbl reveal"{rb}{rf}><thead><tr>{thead}</tr>'
                     f'</thead><tbody>{rows}</tbody></table>')
            if is_mask:
                inner = f'<span class="fxwipe">{inner}</span>'
            parts.append(inner)
        elif t == "card":
            parts.append(f'<div class="card reveal"{rb}{rf}>'
                         f'<div class="c-title">{esc(b.get("title"))}</div>'
                         f'<div class="c-body">{esc(b.get("body"))}</div></div>')
        else:
            sys.exit(f"unknown block type: {t}")
    return "".join(parts)


def slide_html(sk, si, figs_dir):
    s = sk["slides"][si]
    layout = s.get("layout", "full")
    fid = s["id"]
    f = read_figure(s, figs_dir) if s.get("figure") else None
    n = len(sk["slides"])
    pageno = f'<div class="pageno">{si + 1} / {n}</div>'
    t2 = '' if layout == "section" else \
        (' title-2' if est_title_lines(s.get("title"), layout) >= 2 else '')
    open_tag = (f'<section class="slide layout-{layout}'
                + t2
                + (' has-fig' if (f and layout in ("full", "diagram")) else '')
                + '"'
                + f' id="{esc(fid)}"><div class="inner">')
    close = f'{pageno}</div></section>'
    if layout == "section":
        subs = "".join(
            f'<div class="sec-sub reveal"'
            + (f' data-beat="{b["beat"]}"' if b.get("beat") else "")
            + (f' data-fx="{b["fx"]}"' if b.get("fx") else "")
            + f'>{esc(b.get("text"))}</div>'
            for b in s.get("blocks", []) if b.get("type") == "text")
        body = (f'<h1 class="s-title reveal" data-beat="b0" '
                f'data-fx="{s.get("title_fx", "flicker")}">{esc(s.get("title"))}</h1>'
                f'{subs}<div class="sec-rule"></div>')
    else:
        blocks = s.get("blocks", [])
        title = f'<h2 class="s-title reveal" data-beat="b0" data-fx="{s.get("title_fx", "mask")}">{esc(s.get("title"))}</h2>'
        if layout == "diagram" and not blocks:
            # the figure IS the slide (labels live in the figure)
            return open_tag + title + figure_zone_html(f, "diagram-zone") + close
        if layout in ("cards", "grid-5"):
            # title stays in the 0–165 band; .cards zone starts at top 165 (250 with title-2)
            body = title + f'<div class="cards">{blocks_html(blocks)}</div>'
        else:
            zone = "content"
            if f:
                if layout in ("full", "diagram"):
                    body = title + f'<div class="{zone}">{blocks_html(blocks)}</div>' \
                        + figure_zone_html(f, "figure-bottom")
                else:
                    body = title + f'<div class="{zone}">{blocks_html(blocks)}</div>' \
                        + figure_zone_html(f)
            else:
                body = title + f'<div class="{zone}">{blocks_html(blocks)}</div>'
    return open_tag + body + close


def main():
    args = sys.argv[1:]
    theme_path = effects_path = figs_dir = None
    loop = False
    pos = []
    while args:
        a = args.pop(0)
        if a == "--theme":
            theme_path = args.pop(0)
        elif a == "--effects":
            effects_path = args.pop(0)
        elif a == "--figs":
            figs_dir = args.pop(0)
        elif a == "--loop":
            loop = True
        else:
            pos.append(a)
    if len(pos) != 2 or theme_path is None:
        sys.exit(__doc__)
    sk = load_skeleton(pos[0])
    th = load_theme(theme_path)
    theme_dir = os.path.dirname(os.path.abspath(theme_path))

    effects = ""
    if effects_path:
        effects = "\n/* theme effects (factura) */\n" + open(effects_path, encoding="utf-8").read()

    figs_js = {}
    for s in sk["slides"]:
        if s.get("figure") and figs_dir:
            f = read_figure(s, figs_dir)
            if f["frag"]:
                figs_js[s["id"]] = f["frag"]
    figs_map = "".join(
        f'  "{fid}": (function(){{\n{frag}\n    return window.FigTl; }})(),\n'
        for fid, frag in figs_js.items())

    body = "".join(slide_html(sk, i, figs_dir) for i in range(len(sk["slides"])))
    css = VIEWPORT_CSS + "\n" + token_css(th) + "\n" + font_faces(th, theme_dir) \
        + "\n" + CONTENT_CSS + effects
    # loop policy: the loop-free runtime is the default; --loop is the explicit
    # deck-level opt-in (the user's stated policy wins).
    runtime_js = RUNTIME_LOOP_JS if loop else RUNTIME_NOLOOP_JS
    out = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>{esc(sk['meta'].get('title', ''))}</title>
<style>{css}</style>
</head>
<body>
<div class="deck-viewport">
<main class="deck-stage">
{body}
</main>
</div>
<script>/* GSAP (vendored) */
{GSAP_JS}
</script>
<script>
window.__N__ = {len(sk['slides'])};
const FIGS = {{
{figs_map}}};
window.FIGS = FIGS;
{runtime_js}
</script>
</body>
</html>
"""
    with open(pos[1], "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"wrote {pos[1]} ({os.path.getsize(pos[1])} bytes, "
          f"{len(sk['slides'])} slides, {len(figs_js)} figure fragments)")


if __name__ == "__main__":
    main()
