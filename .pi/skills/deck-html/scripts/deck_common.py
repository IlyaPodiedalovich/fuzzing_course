"""Shared helpers for the deck-html scripts (gen_deck.py, assemble.py,
content_check.py). One meaning, one place: the theme-token CSS, the font
embedding, the skeleton loader and the section-tag gate regex live here so
the generator, the assembler and the content gate cannot drift apart.

Scripts stay self-contained inside this skill's scripts/ dir (portability);
they share this module, they do not copy it.
"""
import base64
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# G-1: a well-formed slide section tag. class attribute first, then id.
# The generator emits it, the assembler validates it, the content gate
# fullmatches it — one regex for all three. (data-loop was retired in the
# loop-policy ticket: loop presence is a runtime-variant decision, not a
# section attribute — neither runtime ever read it.)
SECTION_RE = re.compile(
    r'<section class="slide [a-z0-9-]+( [a-z0-9-]+)*" id="[^"]+">')

LATIN_RANGE = "U+0000-00FF, U+2070-209F, U+20AC, U+2122, U+2212, U+FB00-FB06"
CYR_RANGE = "U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116"


def load_skeleton(path):
    with open(path, encoding="utf-8") as f:
        if path.endswith((".yaml", ".yml")):
            try:
                import yaml
            except ImportError:
                sys.exit("PyYAML is required for .yaml skeletons")
            return yaml.safe_load(f)
        return json.load(f)


def load_theme(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def token_css(th):
    keys = ["stage_bg", "slide_bg", "title", "body", "accent", "accent_glow",
            "figfill", "figline", "figtext", "rowalt", "headertext"]
    missing = [k for k in keys if k not in th]
    if missing:
        sys.exit(f"theme tokens missing keys: {', '.join(missing)}")
    # theme keys use underscores; the CSS vars are the hyphenated forms
    # (--slide-bg etc.) — the vendor base and the content template read
    # the hyphenated names (D1: underscores silently fall back to #fff).
    s = ":root{" + "".join(f"--{k.replace('_', '-')}:{th[k]};" for k in keys)
    s += f"--font:{th.get('font_stack', 'sans-serif')};--pad:{th.get('pad', 72)}px;}}"
    return s


def font_faces(th, theme_dir):
    """Base64-embed the theme's font subsets into @font-face rules."""
    faces = []
    fam = th.get("font_family")
    for f in th.get("fonts", []):
        cands = [os.path.join(theme_dir, f["file"]),
                 os.path.join(HERE, "fonts", f["file"])]
        path = next((c for c in cands if os.path.exists(c)), None)
        if path is None:
            sys.exit(f"theme font file not found: {f['file']}")
        b64 = base64.b64encode(open(path, "rb").read()).decode("ascii")
        low = f["file"].lower()
        ur = ""
        if "latin" in low:
            ur = f";unicode-range:{LATIN_RANGE}"
        elif "cyrillic" in low:
            ur = f";unicode-range:{CYR_RANGE}"
        if not ur and not fam:
            sys.exit("font file without subset token needs token 'font_family'")
        faces.append(
            f'@font-face{{font-family:"{fam}";font-style:normal;'
            f'font-weight:{f.get("weight", 400)};'
            f"src:url(data:font/woff2;base64,{b64}) format(\"woff2\"){ur}}}")
    return "".join(faces)
