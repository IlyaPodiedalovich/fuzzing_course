#!/usr/bin/env python3
"""Contract tests for the whitespace contract in the GENERATED route
(ticket 04, review finding: the .ln per-line spans glued into one inline
line — no .ln block rule in the generator base).

Plain-python, no framework. Run:
    python3 skills/deck-html/tests/test_gen_formula.py

A multi-line `fx: type` formula renders as .ln spans, one per skeleton
line; the layout-constants contract requires each line to be a block
(`.ln{display:block}` in CONTENT_CSS). Regression check: the first two
lines' rects must sit on DIFFERENT rendered lines (tops differ) — the
glued-lines bug put them on one.
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "scripts"))
GEN = os.path.join(SCRIPTS, "gen_deck.py")
CONTENT_CHECK = os.path.join(SCRIPTS, "content_check.py")
TEXT_AUDIT = os.path.join(SCRIPTS, "text_audit.py")
THEME = os.path.join(SCRIPTS, "themes", "noir.tokens.json")
EFFECTS = os.path.join(SCRIPTS, "themes", "noir.effects.css")

SKELETON = """skeleton_version: 1
meta:
  title: 'Formula lines'
  audience: test
  lang: ru
  target: html
  canvas: '16:9'
  tone: academic
  anim_role: factual
slides:
- id: s1
  title: 'Typed formula lines'
  layout: full
  blocks:
  - id: a0
    type: formula
    fx: type
    text: |
      line one alpha
      line two beta
      line three gamma
    caption: 'Three typed lines'
  figure: null
"""


def probe_tops(deck):
    """The top coordinate of each .ln line via the runtime ?probe= output."""
    r = subprocess.run([sys.executable, TEXT_AUDIT, deck, "--probe",
                        "#s1 .formula .ln:nth-of-type(1),"
                        "#s1 .formula .ln:nth-of-type(2)"],
                       capture_output=True, text=True)
    tops = []
    for line in r.stdout.splitlines():
        m = re.match(r"PROBE #s1 \.formula \.ln:nth-of-type\(\d\): "
                     r"\[(\d+),(\d+) (\d+),(\d+)\]", line)
        if m:
            tops.append(int(m.group(2)))
    return tops


def main():
    with tempfile.TemporaryDirectory() as root:
        sk = os.path.join(root, "sk.yaml")
        with open(sk, "w", encoding="utf-8") as f:
            f.write(SKELETON)
        deck = os.path.join(root, "deck.html")

        r = subprocess.run([sys.executable, GEN, sk, "--theme", THEME,
                            "--effects", EFFECTS, deck],
                           capture_output=True, text=True)
        assert r.returncode == 0, f"gen_deck failed: {r.stderr}"
        html = open(deck, encoding="utf-8").read()
        assert ".ln{display:block" in html, \
            "the .ln block rule is missing from the generated base"

        r = subprocess.run([sys.executable, CONTENT_CHECK, sk, deck],
                           capture_output=True, text=True)
        assert r.returncode == 0, f"content_check failed:\n{r.stdout}"

        tops = probe_tops(deck)
        assert len(tops) == 2, f"probe did not return both line tops: {tops}"
        assert abs(tops[0] - tops[1]) > 4, \
            f"typed formula lines glued onto one line (tops {tops})"

    print("test_gen_formula: all checks passed")


if __name__ == "__main__":
    main()
