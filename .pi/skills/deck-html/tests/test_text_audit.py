#!/usr/bin/env python3
"""Contract tests for the text collision / overflow gate (F-H3, ticket 02).

Plain-python, no framework. Run: python3 skills/deck-html/tests/test_text_audit.py

Seams:
  1. runtime ?audit=1 mode: the runtime forces every slide to its settled
     pose and writes AUDIT_RESULT JSON into <pre id="audit-out"> (observable
     by the headless dump-dom runner)
  2. scripts/text_audit.py gates on that:
     clean fixture deck            -> exit 0, "GATE text-audit PASS"
     deliberate overlapping pair   -> exit 1, "OVERLAP" + a NAMED selector pair
     deliberate stage overflow     -> exit 1, "OVERLAP"/"OVERFLOW" + named sel
     intentional overlay (data-ov) -> exit 0 (exempt)
"""
import html as htmlmod
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "scripts"))
TEXT_AUDIT = os.path.join(SCRIPTS, "text_audit.py")

sys.path.insert(0, HERE)
sys.path.insert(0, SCRIPTS)
import test_assemble as TA  # fixture + assemble machinery
from text_audit import chromium_args  # one headless invocation, one place


def dump_dom(deck, params="audit=1"):
    r = subprocess.run(chromium_args(f"file://{deck}?{params}",
                                     extra=["--dump-dom"]),
                       capture_output=True, text=True)
    return htmlmod.unescape(r.stdout)


def audit(deck, probe=None):
    cmd = [sys.executable, TEXT_AUDIT, deck]
    if probe:
        cmd += ["--probe", probe]
    return subprocess.run(cmd, capture_output=True, text=True)


OVERLAP_SLIDE = ('<section class="slide full" id="s1">'
                 '<div class="inner"><h2 class="reveal">First content slide</h2>'
                 '<div class="chip a" style="position:absolute;left:200px;top:300px;'
                 'width:300px;height:80px">Alpha overlap line</div>'
                 '<div class="chip b" style="position:absolute;left:250px;top:330px;'
                 'width:300px;height:80px">Beta overlap line</div>'
                 '</div></section>\n')

OVERFLOW_SLIDE = ('<section class="slide full" id="s1">'
                  '<div class="inner"><h2 class="reveal">Overflow slide</h2>'
                  '<div class="oob" style="position:absolute;left:1700px;top:300px;'
                  'width:400px">Push past the right edge</div>'
                  '</div></section>\n')

DATAOV_SLIDE = ('<section class="slide full" id="s1">'
                '<div class="inner"><h2 class="reveal">First content slide</h2>'
                '<div class="chip a" style="position:absolute;left:200px;top:300px;'
                'width:300px;height:80px">Alpha overlap line</div>'
                '<div class="chip b" data-ov style="position:absolute;left:250px;'
                'top:330px;width:300px;height:80px">Beta badge on top</div>'
                '</div></section>\n')

# 2 px grazing (chip b starts 2 px before chip a ends): area > 120 but
# w <= 4 — the grazing tolerance must ignore this (border contact)
GRAZE_SLIDE = ('<section class="slide full" id="s1">'
               '<div class="inner"><h2 class="reveal">First content slide</h2>'
               '<div class="chip a" style="position:absolute;left:200px;top:300px;'
               'width:300px;height:80px">Alpha graze line</div>'
               '<div class="chip b" style="position:absolute;left:498px;top:300px;'
               'width:300px;height:80px">Beta graze line</div>'
               '</div></section>\n')

# chips that overlap chip a but are INVISIBLE in the settled state
# (inline visibility:hidden — what GSAP autoAlpha sets — and computed
# opacity:0) must be excluded from the audit
HIDDEN_SLIDE = ('<section class="slide full" id="s1">'
                '<div class="inner"><h2 class="reveal">First content slide</h2>'
                '<div class="chip a" style="position:absolute;left:200px;top:300px;'
                'width:300px;height:80px">Alpha hidden-overlap line</div>'
                '<div class="chip b" style="position:absolute;left:250px;top:330px;'
                'width:300px;height:80px;visibility:hidden">Ghost hidden</div>'
                '<div class="chip c" style="position:absolute;left:260px;top:340px;'
                'width:300px;height:80px;opacity:0">Ghost transparent</div>'
                '</div></section>\n')


def main():
    with tempfile.TemporaryDirectory() as root:
        sd = TA.build_fixture(root)
        r, out = TA.assemble(root, sd)
        assert r.returncode == 0, f"assemble failed: {r.stderr}"

        # -- 1. runtime ?audit=1 contract: AUDIT_RESULT in the DOM ---------
        dom = dump_dom(out)
        assert "<pre id=\"audit-out\">" in dom, \
            "?audit=1 did not write <pre id=audit-out>"
        assert "AUDIT_RESULT" in dom, "AUDIT_RESULT line missing"

        # -- 2. clean fixture deck passes ----------------------------------
        g = audit(out)
        assert g.returncode == 0, f"clean deck failed: {g.stdout}\n{g.stderr}"
        assert "GATE text-audit PASS" in g.stdout, g.stdout

        # -- 3. deliberate overlap fails with a named selector pair --------
        slides = dict(TA.SLIDES)
        slides["02-s1.html"] = OVERLAP_SLIDE
        with tempfile.TemporaryDirectory() as r2:
            sd2 = TA.build_fixture(r2, slides=slides)
            r, out2 = TA.assemble(r2, sd2)
            assert r.returncode == 0, r.stderr
            g = audit(out2)
            assert g.returncode == 1, f"overlap not caught: {g.stdout}"
            assert "OVERLAP" in g.stdout, g.stdout
            assert "s1 > div.chip.a" in g.stdout \
                and "s1 > div.chip.b" in g.stdout, \
                f"named selector pair missing: {g.stdout}"

        # -- 4. deliberate stage overflow fails, named ---------------------
        slides = dict(TA.SLIDES)
        slides["02-s1.html"] = OVERFLOW_SLIDE
        with tempfile.TemporaryDirectory() as r3:
            sd3 = TA.build_fixture(r3, slides=slides)
            r, out3 = TA.assemble(r3, sd3)
            assert r.returncode == 0, r.stderr
            g = audit(out3)
            assert g.returncode == 1, f"overflow not caught: {g.stdout}"
            assert "OVERFLOW" in g.stdout and "s1 > div.oob" in g.stdout, g.stdout

        # -- 5. data-ov overlay is exempt -----------------------------------
        slides = dict(TA.SLIDES)
        slides["02-s1.html"] = DATAOV_SLIDE
        with tempfile.TemporaryDirectory() as r4:
            sd4 = TA.build_fixture(r4, slides=slides)
            r, out4 = TA.assemble(r4, sd4)
            assert r.returncode == 0, r.stderr
            g = audit(out4)
            assert g.returncode == 0, f"data-ov not exempt: {g.stdout}\n{g.stderr}"

        # -- 6. grazing (<= 4 px in one dimension) is not a collision -------
        slides = dict(TA.SLIDES)
        slides["02-s1.html"] = GRAZE_SLIDE
        with tempfile.TemporaryDirectory() as r5:
            sd5 = TA.build_fixture(r5, slides=slides)
            r, out5 = TA.assemble(r5, sd5)
            assert r.returncode == 0, r.stderr
            g = audit(out5)
            assert g.returncode == 0, f"graze flagged: {g.stdout}\n{g.stderr}"

        # -- 7. settled-invisible text (visibility/opacity) is excluded ----
        slides = dict(TA.SLIDES)
        slides["02-s1.html"] = HIDDEN_SLIDE
        with tempfile.TemporaryDirectory() as r6:
            sd6 = TA.build_fixture(r6, slides=slides)
            r, out6 = TA.assemble(r6, sd6)
            assert r.returncode == 0, r.stderr
            g = audit(out6)
            assert g.returncode == 0, f"settle-invisible flagged: {g.stdout}"

        # -- 8. --probe prints geometry for a named selector ---------------
        g = audit(out, probe="#s1 h2")
        assert g.returncode == 0, g.stdout
        assert "PROBE #s1 h2:" in g.stdout, g.stdout

    print("test_text_audit: all checks passed")


if __name__ == "__main__":
    main()
