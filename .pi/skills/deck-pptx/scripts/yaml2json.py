#!/usr/bin/env python3
"""Convert a YAML skeleton to JSON for the Node generator.

Usage: yaml2json.py <skeleton.yaml> <out.json>
"""
import json
import sys

import yaml

src, dst = sys.argv[1], sys.argv[2]
try:
    with open(src, encoding="utf-8") as f:
        skel = yaml.safe_load(f)
except yaml.YAMLError as e:
    print(f"YAML parse error: {e}")
    print("hint: quote or use a block scalar (|) for strings that contain ': '")
    sys.exit(1)
with open(dst, "w", encoding="utf-8") as f:
    json.dump(skel, f, ensure_ascii=False, indent=2)
print(f"wrote {dst}")
