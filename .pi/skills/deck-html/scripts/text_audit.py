#!/usr/bin/env python3
"""text_audit.py — text collision / overflow gate (F-H3, ticket 02).

usage: text_audit.py <deck.html> [--probe sel1,sel2,...]

Drives the deck's ?audit=1 mode headless (the runtime forces every slide to
its settled pose, then measures every settled-visible leaf text rect —
elements invisible at settle, inline visibility:hidden (GSAP autoAlpha / base
SVG state groups) or opacity 0, are excluded; slide-stack hiddenness is not):
  OVERFLOW — a text leaf outside the 1920x1080 stage
  OVERLAP  — two non-nested text leaves intersect by more than 120 px^2 and
             by more than 4 px in both dimensions (grazing tolerance: borders
             and padding touching is not a text collision)
Gate: exit 0 = 0 problems ("GATE text-audit PASS"), exit 1 = problems, each
named by slide id + selector. Intentional overlay text opts out with data-ov;
--probe prints geometry for named selectors (diagnostics, not a gate).
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
from urllib.parse import quote

CHROME = os.environ.get("CHROME", "chromium-browser")

# The headless invocation shared by the gate and the tests (the chrome flags
# must stay identical — the audit geometry depends on the 1920x1080 1:1 stage).
def chromium_args(url, extra=()):
    return [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
            "--disable-dev-shm-usage", "--force-device-scale-factor=1",
            "--window-size=1920,1080", "--hide-scrollbars",
            "--virtual-time-budget=8000", *list(extra), url]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("deck")
    ap.add_argument("--probe", default="",
                    help="comma-separated CSS selectors for geometry output")
    a = ap.parse_args()
    deck = os.path.realpath(a.deck)
    params = "audit=1"
    if a.probe:
        sels = [s.strip() for s in a.probe.split(",") if s.strip()]
        params += "&probe=" + ",".join(quote(s, safe="") for s in sels)
    url = f"file://{deck}?{params}"
    r = subprocess.run(chromium_args(url, extra=["--dump-dom"]),
                       capture_output=True, text=True)
    dom = html.unescape(r.stdout)  # the dump HTML-escapes the <pre> content
    m = re.search(r"AUDIT_RESULT (\{.*\})", dom)
    if not m:
        print("GATE text-audit FAIL (no AUDIT_RESULT in the dumped DOM)")
        sys.exit("text_audit: the deck must carry the current runtime "
                 "(?audit=1 mode)")
    res = json.loads(m.group(1))
    for line in re.findall(r"^PROBE .*$", dom, re.M):
        print(line)
    n = len(res["problems"])
    if n:
        print(f"GATE text-audit FAIL ({n} problem(s), {res['slides']} slides)")
        for p in res["problems"]:
            print("  " + p)
        sys.exit(1)
    print(f"GATE text-audit PASS ({res['slides']} slides, 0 problems)")


if __name__ == "__main__":
    main()
