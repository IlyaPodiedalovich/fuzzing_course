#!/usr/bin/env python3
"""Heuristic congestion audit for the deck skeleton.

Tracks what the visual review used to catch by eye:
  1. per-slide text fill % (chars vs a per-layout capacity model,
     calibrated on text_fit.py zone capacities at 24px body);
  2. layout-grammar repetition (how many slides share one layout).

Flags: EMPTY (<40% fill), CROWDED (>95%). Use in review: run after every
skeleton change; the fill spread (min..max) and the most repeated layout
are the "скученность" metrics.

Usage: congestion.py <skeleton.yaml>
"""
import sys
from collections import Counter
from pathlib import Path

import yaml

# chars capacity per layout (text zones only; a figure counts as ~200 chars
# of visual content, added in slide_chars)
CAP = {
    "title": 320,
    "section": 140,
    "cards": 1100,
    "full": 1100,
    "content-left": 620,
    "content-right": 620,
    "table": 800,
    "grid-5": 1000,
    "diagram": 300,
}


def slide_chars(sl):
    n = len(sl.get("title", ""))
    for b in sl.get("blocks", []):
        t = b.get("type")
        if t in ("text", "bullet", "formula"):
            n += len(b.get("text", "")) + len(b.get("caption", ""))
        elif t == "card":
            n += len(b.get("title", "")) + len(b.get("body", ""))
        elif t == "table":
            n += sum(len(c) for c in b.get("columns", []))
            n += sum(len(c) for r in b.get("rows", []) for c in r)
    if sl.get("figure"):
        n += 200
    return n


def main(path):
    sk = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    rows = []
    layouts = Counter()
    for sl in sk["slides"]:
        lay = sl.get("layout", "full")
        layouts[lay] += 1
        ch = slide_chars(sl)
        cap = CAP.get(lay, 1000)
        pct = min(100, round(100 * ch / cap))
        rows.append((pct, sl["id"], lay, ch))
    print("slide  layout          chars  fill%  flag")
    for pct, sid, lay, ch in rows:
        flag = "EMPTY" if pct < 40 else ("CROWDED" if pct > 95 else "")
        print(f"{sid:6} {lay:15} {ch:6} {pct:5}%  {flag}")
    print("\nlayout counts:", dict(layouts.most_common()))
    empty = [sid for pct, sid, *_ in rows if pct < 40]
    crowded = [sid for pct, sid, *_ in rows if pct > 95]
    if empty:
        print("EMPTY:", ", ".join(empty))
    if crowded:
        print("CROWDED:", ", ".join(crowded))
    if empty or crowded:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
