#!/usr/bin/env python3
"""Contract tests for scripts/assemble.py (per-slide authoring route, ticket 01).

Plain-python, no framework. Run: python3 skills/deck-html/tests/test_assemble.py

The tests build a 3-slide fixture (title + content + figure) in a temp dir,
assemble it, and check the layer-1/layer-2 contract:
  - single file, no external local references
  - section tags pass content_check's G-1 regex
  - machine CSS (print contract, t-pinned capture rules) is emitted by the
    assembler, not the author
  - FIGS map is syntactically valid JS (dangling-`;` regression) and callable
  - content fidelity: content_check passes against the fixture skeleton
  - guards: FIG/slide-id mismatch, duplicate ids, skeleton order mismatch
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "scripts"))
ASSEMBLE = os.path.join(SCRIPTS, "assemble.py")
CONTENT_CHECK = os.path.join(SCRIPTS, "content_check.py")
RUNTIME = os.path.join(SCRIPTS, "runtime.js")
RUNTIME_NOLOOP = os.path.join(SCRIPTS, "runtime-noloop.js")

sys.path.insert(0, SCRIPTS)
from deck_common import SECTION_RE as G1  # one regex for gate, assembler, tests


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


LOOP_HEADER_OLD = (" * Determinism: no random, no Date.now. Loop = deck-level restart (T-14),\n"
                   " * figure slides only, cleared on navigation / capture / print.")
LOOP_HEADER_NEW = (" * Determinism: no random, no Date.now. No loops: the only animation trigger\n"
                   " * is slide activation (play once, never replay).")
LOOP_TOP_OLD = "/* deck-html runtime (D2) — inlined by gen_deck.py after the FIGS map."
LOOP_TOP_NEW = ("/* deck-html runtime (D2, loop-free) — inlined by assemble.py (per-slide\n"
                " * authoring route) after the FIGS map; also usable via --runtime from the\n"
                " * generated route.")
LOOP_TIMER_DECL = "  let loopTimer = null;\n  let figTimer = null;"
LOOP_TIMER_KILL = "    if (loopTimer) { clearTimeout(loopTimer); loopTimer = null; }\n"
LOOP_REPLAY = """      b.fig.eventCallback("onComplete", function () {
        if (frozen || i !== idx) return;
        loopTimer = setTimeout(function () {
          if (!frozen && i === idx) playSlide(i); // T-14: hold, then replay
        }, 1500);
      });
"""


def noloop_from_runtime(src):
    """The documented derivation of runtime-noloop.js from runtime.js — the
    sync test asserts the pair differs ONLY by this loop wiring."""
    for old, new in ((LOOP_TOP_OLD, LOOP_TOP_NEW), (LOOP_HEADER_OLD, LOOP_HEADER_NEW),
                     (LOOP_TIMER_DECL, "  let figTimer = null;")):
        assert old in src, f"sync test drift: {old[:40]!r} not in runtime.js"
        src = src.replace(old, new)
    for chunk in (LOOP_TIMER_KILL, LOOP_REPLAY):
        assert chunk in src, f"sync test drift: {chunk[:40]!r} not in runtime.js"
        src = src.replace(chunk, "")
    return src

TOKENS = {
    "stage_bg": "#072018", "slide_bg": "#0F3B2C", "title": "#EAD0AC",
    "body": "#EAD0AC", "accent": "#D98C53", "accent_glow": "rgba(217,140,83,.25)",
    "figfill": "#0B3124", "figline": "#B87333", "figtext": "#D9C7A4",
    "rowalt": "#0C3529", "headertext": "#0F3B2C",
    "font_stack": "'Courier New', monospace", "pad": 64,
    "font_family": "Montserrat",
    "fonts": [
        {"file": "montserrat-latin-400-normal.woff2", "weight": 400},
        {"file": "montserrat-cyrillic-400-normal.woff2", "weight": 400},
    ],
}
STYLES = ".inner{position:absolute;inset:0;padding:var(--pad)}\n"
SKELETON = """skeleton_version: 1
meta:
  title: 'Test Deck'
  audience: test
  lang: ru
  target: html
  canvas: '16:9'
  tone: academic
  anim_role: factual
slides:
- id: t
  title: 'Test title slide'
  layout: section
  blocks:
  - id: a0
    type: text
    text: 'Route under test'
  figure: null
- id: s1
  title: 'First content slide'
  layout: full
  blocks:
  - id: a0
    type: text
    text: 'Line one of the content'
  figure: null
- id: s2
  title: 'Figure slide'
  layout: full
  blocks:
  - id: a0
    type: text
    text: 'Text next to the figure'
  figure:
    kind: diagram
    prompt: 'a test figure'
"""
SLIDES = {
    "01-t.html": '<section class="slide title" id="t">'
                 '<div class="inner"><h1 class="reveal">Test title slide</h1>'
                 '<p class="reveal">Route under test</p></div></section>\n',
    "02-s1.html": '<section class="slide full" id="s1">'
                  '<div class="inner"><h2 class="reveal">First content slide</h2>'
                  '<p class="reveal">Line one of the content</p></div></section>\n',
    "03-s2.html": '<section class="slide full has-fig" id="s2">'
                  '<div class="inner"><h2 class="reveal">Figure slide</h2>'
                  '<p class="reveal">Text next to the figure</p>'
                  '<div class="fig"><!--FIG:s2--></div></div></section>\n',
}
FIG_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50">' \
          '<rect id="fs2-box" width="100" height="50" fill="currentColor"/></svg>\n'
FIG_TL = """window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  tl.fromTo("#fs2-box", { opacity: 0 }, { opacity: 1, duration: 0.5 });
  return tl;
};
"""


def build_fixture(root, slides=None):
    slides = slides or SLIDES
    sd = os.path.join(root, "slides")
    os.makedirs(sd)
    for name, body in slides.items():
        with open(os.path.join(sd, name), "w", encoding="utf-8") as f:
            f.write(body)
    with open(os.path.join(root, "tokens.json"), "w", encoding="utf-8") as f:
        json.dump(TOKENS, f)
    with open(os.path.join(root, "styles.css"), "w", encoding="utf-8") as f:
        f.write(STYLES)
    with open(os.path.join(root, "skeleton.yaml"), "w", encoding="utf-8") as f:
        f.write(SKELETON)
    ad = os.path.join(root, "assets")
    os.makedirs(ad)
    with open(os.path.join(ad, "fig-s2.svg"), "w", encoding="utf-8") as f:
        f.write(FIG_SVG)
    with open(os.path.join(ad, "fig-s2.tl.js"), "w", encoding="utf-8") as f:
        f.write(FIG_TL)
    return sd


def assemble(root, sd, extra=()):
    out = os.path.join(root, "deck.html")
    cmd = [sys.executable, ASSEMBLE, sd, out,
           "--tokens", os.path.join(root, "tokens.json"),
           "--styles", os.path.join(root, "styles.css"),
           "--figs", os.path.join(root, "assets"),
           "--skeleton", os.path.join(root, "skeleton.yaml")] + list(extra)
    return subprocess.run(cmd, capture_output=True, text=True), out


def figs_block(html):
    m = re.search(r"<script>\s*(window\.__N__.*?)</script>", html, re.S)
    assert m, "FIGS/counter script block not found"
    return m.group(1).strip()


def node_run(js, label):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                     encoding="utf-8") as f:
        f.write("globalThis.window = globalThis;\n" + js)
        p = f.name
    try:
        r = subprocess.run(["node", p], capture_output=True, text=True)
        assert r.returncode == 0, f"{label}: node failed:\n{r.stderr}"
        return r.stdout
    finally:
        os.unlink(p)


def main():
    with tempfile.TemporaryDirectory() as root:
        sd = build_fixture(root)

        # -- 1. happy path -------------------------------------------------
        r, out = assemble(root, sd)
        assert r.returncode == 0, f"assemble failed: {r.stderr}"
        html = open(out, encoding="utf-8").read()

        # single file, no external local references
        assert not re.search(r"<link\b", html), "external <link> found"
        ext = re.findall(r'(?:src|href)\s*=\s*["\'](?!data:)[^"\']*', html)
        assert not ext, f"external references: {ext}"

        # sections + G-1 regex
        tags = re.findall(r"<section\b[^>]*>", html)
        assert len(tags) == 3, f"expected 3 sections, got {len(tags)}"
        for t in tags:
            assert G1.fullmatch(t), f"G-1 regex fails on: {t}"

        # machine layer emitted by the assembler
        assert "@page{size:1920px 1080px;margin:0}" in html, "F-P1 @page missing"
        assert ".flow-el{display:none!important" in html, "print contract missing"
        assert "html.t-pinned .slide{transition:none!important}" in html, "t-pinned rule missing"
        assert "--slide-bg:#0F3B2C" in html, "tokens :root not inlined"
        # single-file promise: the theme's font subsets are base64-embedded
        assert html.count("data:font/woff2;base64,") == 2, "font subsets not embedded"

        # runtime default = loop-free (activation-only) — behavioral markers,
        # not comment text: the T-14 loop wiring must be absent
        assert "loopTimer" not in html, "default runtime is not loop-free"

        # figure inlined, no leftover markers
        assert "fs2-box" in html and "<!--FIG" not in html, "figure inlining failed"

        # -- 2. FIGS block: syntax + callable (dangling-`;` regression) ----
        block = figs_block(html)
        node_run(block, "FIGS syntax")
        stub = block + """
const gsap = { timeline: (o) => ({ fromTo: () => {}, duration: () => 1 }) };
const tl = window.FIGS["s2"](gsap);
if (!tl) { throw new Error("FIGS.s2 did not return a timeline"); }
console.log("FIGS-OK");
"""
        assert "FIGS-OK" in node_run(stub, "FIGS call")

        # -- 3. content fidelity -------------------------------------------
        r = subprocess.run([sys.executable, CONTENT_CHECK,
                            os.path.join(root, "skeleton.yaml"), out],
                           capture_output=True, text=True)
        assert r.returncode == 0, f"content_check failed:\n{r.stdout}{r.stderr}"

        # -- 4. guard: FIG marker must match the section id ----------------
        bad = dict(SLIDES)
        bad["03-s2.html"] = bad["03-s2.html"].replace("FIG:s2", "FIG:zz")
        with tempfile.TemporaryDirectory() as r2:
            sd2 = build_fixture(r2, slides=bad)
            r, _ = assemble(r2, sd2)
            assert r.returncode != 0, "FIG/slide-id mismatch not caught"
            assert "mismatch" in r.stderr.lower(), r.stderr

        # -- 5. guard: duplicate slide id ----------------------------------
        dup = dict(SLIDES)
        dup["02-s1.html"] = dup["02-s1.html"].replace('id="s1"', 'id="t"')
        with tempfile.TemporaryDirectory() as r3:
            sd3 = build_fixture(r3, slides=dup)
            r, _ = assemble(r3, sd3)
            assert r.returncode != 0, "duplicate slide id not caught"
            assert "duplicate" in r.stderr.lower(), r.stderr

        # -- 6. guard: file order must match skeleton order ----------------
        with tempfile.TemporaryDirectory() as r4:
            sd4 = build_fixture(r4)
            # skeleton order is t, s1, s2 -> files must be NN-t, NN-s1, NN-s2
            os.rename(os.path.join(sd4, "01-t.html"), os.path.join(sd4, "03-t.html"))
            r, _ = assemble(r4, sd4)
            assert r.returncode != 0, "skeleton order mismatch not caught"
            assert "order" in r.stderr.lower(), r.stderr

        # -- 7a. guard: duplicate figure element id across figures --------
        bad = dict(SLIDES)
        bad["04-s3.html"] = ('<section class="slide full has-fig" id="s3">'
                             '<div class="inner">'
                             '<h2 class="reveal">Second figure</h2>'
                             '<div class="fig"><!--FIG:s3--></div>'
                             '</div></section>\n')
        with tempfile.TemporaryDirectory() as r5:
            sd5 = build_fixture(r5, slides=bad)
            ad = os.path.join(r5, "assets")
            with open(os.path.join(ad, "fig-s3.svg"), "w", encoding="utf-8") as f:
                f.write('<svg xmlns="http://www.w3.org/2000/svg" '
                        'viewBox="0 0 100 50">'
                        '<rect id="fs2-box" width="100" height="50"/>'
                        '</svg>\n')
            with open(os.path.join(ad, "fig-s3.tl.js"), "w", encoding="utf-8") as f:
                f.write("window.FigTl = (gsap) => {\n"
                        "  return gsap.timeline({ paused: true });\n"
                        "};\n")
            r, _ = assemble(r5, sd5)
            assert r.returncode != 0, "duplicate figure element id not caught"
            assert "fs2-box" in r.stderr, r.stderr

        # -- 7. --runtime selects the loop-capable runtime ------------------
        r, out = assemble(root, sd, extra=["--runtime", RUNTIME])
        assert r.returncode == 0, r.stderr
        html = open(out, encoding="utf-8").read()
        assert "loopTimer" in html, "loop runtime not inlined via --runtime"

    # -- 8. runtime pair sync: noloop == runtime minus the T-14 wiring ------
    assert rd(RUNTIME_NOLOOP) == noloop_from_runtime(rd(RUNTIME)), \
        "runtime-noloop.js has drifted from runtime.js (re-derive or update " \
        "the sync test together)"

    print("test_assemble: all checks passed")


if __name__ == "__main__":
    main()
