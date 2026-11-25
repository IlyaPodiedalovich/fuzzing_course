#!/usr/bin/env python3
"""Contract tests for the content-geometry gate in render_html.sh
(F-H5, ticket 03).

Plain-python, no framework. Run: python3 skills/deck-html/tests/test_render_gate.py

R3 proves byte-stability of ONE frame — a stable background-only frame is
green. The gate: every settled capture (s<i>-t1.png) must carry real content
(grayscale stddev above the threshold). The regression fixture injects
section.slide{position:relative} into the theme CSS — the stacked-slides bug
class (mechanism and the effects-CSS rule: gotchas F-H5); the stage then
shows only the first slide, every non-first settled frame is uniform, and
the PDF is unaffected (print CSS re-describes the stack) — exactly why the
old gate chain stayed green on the bug.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "scripts"))
RENDER = os.path.join(SCRIPTS, "render_html.sh")

sys.path.insert(0, HERE)
import test_assemble as TA  # fixture + assemble machinery


def render(deck, qa, n=3):
    return subprocess.run(["bash", RENDER, deck, qa, str(n)],
                          capture_output=True, text=True)


def main():
    # -- 1. clean fixture deck passes the content-geometry gate ------------
    with tempfile.TemporaryDirectory() as root:
        sd = TA.build_fixture(root)
        r, out = TA.assemble(root, sd)
        assert r.returncode == 0, f"assemble failed: {r.stderr}"
        qa = os.path.join(root, "qa")
        g = render(out, qa, 3)
        assert g.returncode == 0, f"clean render failed: {g.stdout}\n{g.stderr}"
        assert "GATE visible-content PASS" in g.stdout, g.stdout

    # -- 2. the position:relative regression fails, naming the slides ------
    with tempfile.TemporaryDirectory() as root:
        sd = TA.build_fixture(root)
        with open(os.path.join(root, "styles.css"), "a", encoding="utf-8") as f:
            # the exact regression (build-issues #4): (0,1,1) beats the
            # vendor .slide{position:absolute;inset:0} (0,1,0)
            f.write("section.slide{position:relative}\n")
        r, out = TA.assemble(root, sd)
        assert r.returncode == 0, f"assemble failed: {r.stderr}"
        qa = os.path.join(root, "qa")
        g = render(out, qa, 3)
        assert g.returncode != 0, f"broken deck passed: {g.stdout}"
        assert "visible-content FAIL" in g.stdout, g.stdout
        # slides 2..N sit off-stack behind the first → uniform frames
        assert "slide 2" in g.stdout, f"failing slide not named: {g.stdout}"

    print("test_render_gate: all checks passed")


if __name__ == "__main__":
    main()
