#!/usr/bin/env python3
"""Text-fit check hook for JSON skeletons (ticket 04).

Estimates whether the text volume of each slide field fits the layout field
at the design canvas (1280x720) using layout-discipline constants:
margins ~4.5%, title zone, footer rail, body font size.

Model (deliberately simple, ±30% accuracy is the goal):
  - char width  = 0.52 * font_size (Cyrillic average)
  - line height = 1.35 * font_size
  - safety      = 85% of geometric capacity counts as usable

Usage: text_fit.py <skeleton.json>
Exit code: 0 = all OK, 1 = at least one WARN (tight), 2 = at least one OVER.
"""
import json, sys
import yaml
import math
import sys

W, H = 1280, 720
MARGIN = int(0.045 * W)          # ~58 px
GUTTER = 40
TITLE_ZONE = 96                   # title + spacing
FOOTER_RAIL = 36
FIG_SHARE = 0.45                  # fraction of content width given to a figure
BODY_FS = 24
SMALL_FS = 18                     # tables, cards
WARN = 0.85
OVER = 1.0


def field_capacity(width, height, fs):
    if width <= 0 or height <= 0:
        return 0
    cpl = max(1, int(width / (0.52 * fs)))
    lines = max(1, int(height / (1.35 * fs)))
    return int(lines * cpl * WARN)


def text_col_box(layout):
    """Content box for text blocks, by layout."""
    cw = W - 2 * MARGIN
    ch = H - 2 * MARGIN - TITLE_ZONE - FOOTER_RAIL
    if layout in ("content-left", "content-right"):
        return int(cw * (1 - FIG_SHARE) - GUTTER), ch
    if layout == "grid-5":
        card_w = (cw - 4 * GUTTER) // 5
        return card_w, int(ch * 0.9)
    # full / table
    return cw, ch


def check(skel):
    status = {"ok": 0, "warn": 0, "over": 0}
    problems = []

    def judge(label, used, cap):
        if cap <= 0:
            status["over"] += 1
            problems.append(f"{label}: no space (used {used})")
            return
        ratio = used / cap
        if ratio > OVER:
            status["over"] += 1
            problems.append(f"{label}: OVER {used}/{cap} chars ({ratio:.0%})")
        elif ratio > WARN:
            status["warn"] += 1
            problems.append(f"{label}: WARN {used}/{cap} chars ({ratio:.0%})")
        else:
            status["ok"] += 1

    for slide in skel["slides"]:
        sid, layout = slide["id"], slide["layout"]
        tw, th = text_col_box(layout)
        cap = field_capacity(tw, th, BODY_FS)
        print(f"{sid} ({layout}): text field {tw}x{th}px, body {BODY_FS}px "
              f"-> ~{cap} chars")

        table_block = next((b for b in slide.get("blocks", []) if b["type"] == "table"), None)
        if table_block:
            # table model: rows x row-height; cells must fit their column width
            n_rows = len(table_block["rows"])
            row_h = 1.35 * SMALL_FS + 8
            avail_rows = int(th / row_h)
            judge(f"{sid} rows", n_rows, avail_rows)
            if n_rows > avail_rows:
                problems.append(f"  {sid}: {n_rows} rows > {avail_rows} fit at {SMALL_FS}px")
            cols = len(table_block["columns"])
            col_w = (tw - (cols - 1) * 8) / cols
            cpl = max(1, int(col_w / (0.52 * SMALL_FS)))
            for r, row in enumerate(table_block["rows"]):
                for c, cell in enumerate(row):
                    if len(cell) > cpl:
                        status["over"] += 1
                        problems.append(f"  {sid} cell r{r}c{c}: {len(cell)} chars > {cpl} fit "
                                        f"({cell!r})")
                    elif len(cell) > 0.85 * cpl:
                        status["warn"] += 1
                        problems.append(f"  {sid} cell r{r}c{c}: {len(cell)}/{cpl} chars "
                                        f"({cell!r}) tight")
            continue

        n = len(slide.get("blocks", []))
        for b in slide.get("blocks", []):
            if b["type"] == "table":
                continue
            fs = SMALL_FS if layout == "grid-5" else BODY_FS
            text = b.get("text") or b.get("body") or ""
            if b["type"] == "card":
                text = (b.get("title", "") + " " + b.get("body", ""))
                fs = SMALL_FS
            # each block is judged against its share of the field
            share = field_capacity(tw, th, fs) // max(1, n)
            judge(f"{sid}:{b['id']}", len(text), share)

    print()
    for p in problems:
        print(p)
    total = sum(status.values())
    print(f"\nResult: {total} fields — {status['ok']} OK, {status['warn']} WARN, {status['over']} OVER")
    return 2 if status["over"] else (1 if status["warn"] else 0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: text_fit.py <skeleton.json>")
    path = sys.argv[1]
    try:
        with open(path, encoding="utf-8") as f:
            skel = yaml.safe_load(f) if path.endswith((".yaml", ".yml")) else json.load(f)
    except yaml.YAMLError as e:
        print(f"YAML parse error: {e}")
        print("hint: quote or use a block scalar (|) for strings that contain ': '")
        sys.exit(1)
    sys.exit(check(skel))
