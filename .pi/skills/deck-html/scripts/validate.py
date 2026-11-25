#!/usr/bin/env python3
"""Validate a presentation skeleton (schema v1.1 + cross-checks).

Usage: validate.py <skeleton.yaml>
Exit: 0 = clean, 1 = schema error(s), 2 = cross-check error(s).
"""
import json
import sys
from pathlib import Path

import yaml
import jsonschema

SKILL = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((SKILL / "references" / "schema.json").read_text(encoding="utf-8"))


def cross_checks(skel):
    ok = True
    for sl in skel.get("slides", []):
        sid = sl.get("id", "?")
        # block ids unique within the slide
        bids = [b["id"] for b in sl.get("blocks", [])]
        dups = sorted({i for i in bids if bids.count(i) > 1})
        if dups:
            print(f"X {sid}: duplicate block ids {dups}")
            ok = False
        # anim beat table discipline
        anim = sl.get("anim")
        if anim:
            ab = [b["id"] for b in anim.get("beats", [])]
            dups = sorted({i for i in ab if ab.count(i) > 1})
            if dups:
                print(f"X {sid}: duplicate beat ids {dups}")
                ok = False
            if not ab or ab[0] != "b0":
                print(f"X {sid}: beats must start at b0 (got {ab[:1]})")
                ok = False
            nums = [int(i[1:]) for i in ab]
            if nums != sorted(nums):
                print(f"X {sid}: beat ids out of order: {ab}")
                ok = False
        # notes on content slides is a hint, not an error
    # slide count sanity against the stated count is the agent's job (coverage)
    return ok


def main(path):
    p = Path(path)
    if not p.exists():
        print(f"no such file: {path}")
        return 1
    try:
        skel = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"YAML parse error: {e}")
        print("hint: quote or use a block scalar (|) for strings that contain ': '")
        return 1
    v = jsonschema.Draft202012Validator(SCHEMA)
    errors = sorted(v.iter_errors(skel), key=lambda e: list(e.path))
    if errors:
        for e in errors:
            print(f"SCHEMA {'.'.join(map(str, e.path))}: {e.message}")
        return 1
    ok = cross_checks(skel)
    n = len(skel.get("slides", []))
    anim_n = sum(1 for s in skel.get("slides", []) if s.get("anim"))
    fig_n = sum(1 for s in skel.get("slides", []) if s.get("figure"))
    print(f"OK: {n} slides, {anim_n} with anim, {fig_n} with figure")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
