#!/usr/bin/env python3
"""type_floor.py — body font-size floor audit (retro-2 ticket 03).

Scans the CSS of a built deck — one single-file deck.html (all CSS inlined)
or a set of files (.css themes/effects + slide .html files) — for font-size
declarations below the body floor: 25 px at 1920x1080 (references/
layout-constants.md, type scale). Each sub-floor rule that is NOT chrome is
named (selector + file + line) as a REVIEW WARNING. Not a hard gate: exit 0
always (1 = unreadable input).

Chrome — exempted by the CHROME token whitelist (the authority): table
cells, figure/card captions, page numbers, kickers/badges/labels, code
windows, figure placeholders, headings. A body class below the floor is a
theme defect: raise it in the theme CSS, never tolerate it.

Usage: type_floor.py <deck.html | file.css file.html ...>
"""
import os
import re
import sys

FLOOR = 25  # px, flowing body text at 1920x1080

# chrome tokens (class names without the dot, or tag names)
CHROME = {
    # tables
    "tbl", "th", "td",
    # figure/card captions
    "fcap", "f-cap", "figcaption", "caption", "tcap", "figcap",
    # page number
    "pageno",
    # kickers / badges / labels
    "kicker", "t-kicker", "sec-kicker", "badge", "ch-head", "critline",
    "q-src", "k",  # .k = chip row key (a label)
    # figure placeholders / labels
    "fig-ph", "fig-prompt", "fig-label",
    # code windows
    "code", "pre",
    # headings
    "c-title", "s-title", "h1", "h2", "h3",
}

SIZE_RE = re.compile(r"font-size:\s*([0-9]+(?:\.[0-9]+)?)\s*(px|em|rem|%)")


def css_rules(text, base=0):
    """yield (selector, body, selector_offset) for each CSS rule; @-rules
    (e.g. @media) are recursed; offsets are absolute in the outermost text."""
    i, n = 0, len(text)
    while i < n:
        b = text.find("{", i)
        if b == -1:
            break
        sel = text[i:b].strip()
        depth, j = 1, b + 1
        while j < n and depth:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1
        body = text[b + 1:j - 1]
        if sel.startswith("@"):
            yield from css_rules(body, base + b + 1)
        elif sel:
            yield sel, body, base + i
        i = j


def tokens(selector):
    out = set()
    for part in selector.split(","):
        for tok in re.split(r"[\s.>~+\[\]:]+", part.strip()):
            if tok and tok != "*":
                out.add(tok)
    return out


class Scan:
    def __init__(self):
        self.warnings = []
        self.nonpx = 0

    def css(self, css, first_line, path):
        for sel, body, at in css_rules(css):
            fm = SIZE_RE.search(body)
            if not fm:
                continue
            size, unit = float(fm.group(1)), fm.group(2)
            if unit != "px":
                self.nonpx += 1
                continue
            if size < FLOOR and not (tokens(sel) & CHROME):
                self.warnings.append(
                    (path, first_line + css[:at].count("\n"), f"{sel} {size:g}px"))

    def html(self, html, path):
        for m in re.finditer(r"<style[^>]*>(.*?)</style>", html, re.S):
            css, off = m.group(1), m.start(1)
            self.css(css, html[:off].count("\n") + 1, path)
        for m in re.finditer(r"<([a-zA-Z][a-zA-Z0-9]*)((?:[^>\"']|'[^']*')*?)\bstyle=\"([^\"]*)\"", html):
            tag, attrs, style = m.group(1), m.group(2), m.group(3)
            fm = SIZE_RE.search(style)
            if not fm:
                continue
            size, unit = float(fm.group(1)), fm.group(2)
            if unit != "px":
                self.nonpx += 1
                continue
            cls = re.search(r"class=\"([^\"]*)\"", attrs)
            toks = ({tag} | set(cls.group(1).split())) if cls else {tag}
            if size < FLOOR and not (toks & CHROME):
                self.warnings.append(
                    (path, html[:m.start()].count("\n") + 1, f"<{tag}> inline {size:g}px"))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    paths = sys.argv[1:]
    scan = Scan()
    for p in paths:
        if not os.path.exists(p):
            sys.exit(f"type_floor: no such file: {p}")
        text = open(p, encoding="utf-8").read()
        if p.endswith(".css"):
            scan.css(text, 1, p)
        else:
            scan.html(text, p)

    print(f"type_floor: body floor = {FLOOR}px @ 1920x1080, {len(paths)} file(s)")
    if scan.nonpx:
        print(f"  note: {scan.nonpx} non-px font-size declaration(s) — check by hand")
    if scan.warnings:
        print(f"REVIEW WARNING: {len(scan.warnings)} sub-floor rule(s) — raise them in the theme:")
        for path, line, what in sorted(scan.warnings):
            print(f"  {what}  ({os.path.basename(path)}:{line})")
    else:
        print("no sub-floor body rule (chrome whitelisted) — 0 warnings")
    sys.exit(0)  # review warnings, not a hard gate


if __name__ == "__main__":
    main()
