#!/usr/bin/env python3
"""Acceptance for the documented content_check substring rule
(layout-constants.md, ticket 05): the recipe applied to a fresh 6-line
block keeps the gate green; a label injected between the field's lines is
red and named.

Plain-python, no framework. Run:
    python3 skills/deck-html/tests/test_content_check_contract.py
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "scripts"))
CONTENT_CHECK = os.path.join(SCRIPTS, "content_check.py")

SKELETON = """skeleton_version: 1
meta:
  title: 'Substring contract'
  audience: test
  lang: ru
  target: html
  canvas: '16:9'
  tone: academic
  anim_role: factual
slides:
- id: s1
  title: 'Six lines'
  layout: full
  blocks:
  - id: a0
    type: text
    text: |
      alpha line one
      beta line two
      gamma line three
      delta line four
      epsilon line five
      zeta line six
  figure: null
"""

# Recipe: the 6 lines split into separate elements, SAME ORDER — green.
GREEN_HTML = """<!doctype html><html lang="ru"><head><meta charset="utf-8"></head><body>
<div class="deck-stage"><div class="deck">
<section class="slide full" id="s1"><div class="inner">
<h2>Six lines</h2>
<p>alpha line one</p><p>beta line two</p><p>gamma line three</p>
<p>delta line four</p><p>epsilon line five</p><p>zeta line six</p>
</div></section>
</div></div>
</body></html>
"""

# Red case: a label injected BETWEEN the field's lines — the field's
# contiguous substring breaks and the gate names the field.
RED_HTML = """<!doctype html><html lang="ru"><head><meta charset="utf-8"></head><body>
<div class="deck-stage"><div class="deck">
<section class="slide full" id="s1"><div class="inner">
<h2>Six lines</h2>
<p>alpha line one</p><p>beta line two</p><p class="head">MID-LABEL</p>
<p>gamma line three</p><p>delta line four</p><p>epsilon line five</p><p>zeta line six</p>
</div></section>
</div></div>
</body></html>
"""

# Sub-item convention (skeleton-format.md, retro-2 ticket 03): an indented
# line (exactly two leading spaces) inside a bullet block is a sub-item.
# The gate must NOT reject it — indentation is line structure, not text.
SUB_SKELETON = """skeleton_version: 1
meta:
  title: 'Sub items'
  audience: test
  lang: ru
  target: html
  canvas: '16:9'
  tone: academic
  anim_role: factual
slides:
- id: s1
  title: 'Sub items'
  layout: full
  blocks:
  - id: a0
    type: bullet
    text: |
      parent line one
        child line two
      parent line three
  figure: null
"""

GREEN_SUB_HTML = """<!doctype html><html lang="ru"><head><meta charset="utf-8"></head><body>
<div class="deck-stage"><div class="deck">
<section class="slide full" id="s1"><div class="inner">
<h2>Sub items</h2>
<ul class="b"><li>parent line one</li><li class="sub">child line two</li><li>parent line three</li></ul>
</div></section>
</div></div>
</body></html>
"""


def run(html, skeleton=SKELETON):
    with tempfile.TemporaryDirectory() as root:
        sk = os.path.join(root, "sk.yaml")
        with open(sk, "w", encoding="utf-8") as f:
            f.write(skeleton)
        deck = os.path.join(root, "deck.html")
        with open(deck, "w", encoding="utf-8") as f:
            f.write(html)
        r = subprocess.run([sys.executable, CONTENT_CHECK, sk, deck],
                           capture_output=True, text=True)
        return r.returncode, r.stdout


def main():
    rc, out = run(GREEN_HTML)
    assert rc == 0, f"recipe (split lines, same order) must pass:\n{out}"
    assert "PASS" in out, out

    rc, out = run(RED_HTML)
    assert rc != 0, "injected label between the field's lines must FAIL"
    assert "MID-LABEL" not in out or "FAIL" in out, out
    assert "a0" in out, f"the failing field must be named:\n{out}"

    # Indented sub-line (two leading spaces) passes the gate — the rendered
    # markup may carry any whitespace, the line text must survive.
    rc, out = run(GREEN_SUB_HTML, SUB_SKELETON)
    assert rc == 0, f"an indented sub-line must pass the gate:\n{out}"
    assert "PASS" in out, out

    print("test_content_check_contract: all checks passed")


if __name__ == "__main__":
    main()
