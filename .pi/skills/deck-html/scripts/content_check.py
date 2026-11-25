#!/usr/bin/env python3
"""deck-html content QA (the markitdown equivalent for HTML).

Compares every text field of the skeleton against the generated deck.html:
missing texts, placeholder leftovers, figure-prompt leaks, external references
(single-file rule).

usage: content_check.py <skeleton.yaml|json> <deck.html>
exit: 0 = clean, 1 = problem(s) found
"""
import sys
import re
import json
import html as _html

from deck_common import SECTION_RE, load_skeleton  # one regex + one loader
# for gate, assembler and generator


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def expected_texts(slide):
    """slide -> list of (where, text) that MUST appear in the slide's HTML."""
    exp = [("title", slide.get("title", ""))]
    for b in slide.get("blocks", []):
        t = b["type"]
        if t == "bullet":
            exp += [(f"bullet:{b.get('id')}", l.strip())
                    for l in (b.get("text") or "").splitlines() if l.strip()]
        elif t == "text":
            exp.append((f"text:{b.get('id')}", b.get("text", "")))
        elif t == "formula":
            exp.append((f"formula:{b.get('id')}", b.get("text", "")))
            if b.get("caption"):
                exp.append((f"formula-cap:{b.get('id')}", b["caption"]))
        elif t == "table":
            exp += [(f"th:{b.get('id')}", c) for c in b.get("columns", [])]
            for ri, r in enumerate(b.get("rows", [])):
                for ci, c in enumerate(r):
                    exp.append((f"td:{b.get('id')}[{ri}][{ci}]", c))
        elif t == "card":
            exp.append((f"card-title:{b.get('id')}", b.get("title", "")))
            exp.append((f"card-body:{b.get('id')}", b.get("body", "")))
    fig = slide.get("figure") or {}
    if fig.get("caption"):
        exp.append(("figure-caption", fig["caption"]))
    return [(w, t) for w, t in exp if norm(t)]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sk = load_skeleton(sys.argv[1])
    html = open(sys.argv[2], encoding="utf-8").read()

    # single-file rule: no external references
    ext = re.findall(r'(?:src|href)\s*=\s*["\'](?:https?:|//|file:|/)[^"\']*', html)
    problems = []
    for m in ext:
        problems.append(f"external reference (single-file rule): {m[:80]}")

    # G-1: every <section> tag must be well-formed. A misplaced closing quote in the
    # class attribute silently turns conditional classes (title-2, has-fig)
    # into bare boolean attributes — text checks pass, layout rules never apply.
    # The regex is deck_common.SECTION_RE (one source for gate, assembler,
    # generator — gotchas G-1).
    for m in re.finditer(r"<section\b[^>]*>", html):
        tag = m.group(0)
        if not SECTION_RE.fullmatch(tag):
            problems.append(f"malformed section tag (class attribute?): {tag[:100]}")

    sections = dict(re.findall(
        r'<section[^>]*id="([^"]+)"[^>]*>(.*?)</section>', html, re.S))

    for s in sk["slides"]:
        fid = s["id"]
        sec = sections.get(fid)
        if sec is None:
            problems.append(f"{fid}: section missing from the deck")
            continue
        hay = norm(_html.unescape(re.sub(r"<[^>]+>", " ", sec)))
        for where, txt in expected_texts(s):
            if norm(txt) not in hay:
                problems.append(f"{fid}: missing {where}: «{txt[:60]}»")
        fig = s.get("figure") or {}
        if fig.get("prompt") and norm(fig["prompt"])[:40] in hay:
            problems.append(f"{fid}: figure prompt leaked into the slide (spec, not content)")

    if 'class="fig-prompt"' in html:
        problems.append("placeholder figure panel present (figure assets missing?)")

    if problems:
        print("CONTENT CHECK: FAIL")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print(f"CONTENT CHECK: PASS ({len(sk['slides'])} slides, "
          f"{sum(len(expected_texts(s)) for s in sk['slides'])} text fields verified)")


if __name__ == "__main__":
    main()
