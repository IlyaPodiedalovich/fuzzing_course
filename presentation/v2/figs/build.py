#!/usr/bin/env python3
"""build all v2 figure assets: python3 presentation/v2/figs/build.py"""
import figs_a  # noqa: F401  (registers s1 .. s14)
import figs_b  # noqa: F401  (registers s15 .. s30)
import figlib

if __name__ == "__main__":
    figlib.write_all()
