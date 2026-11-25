#!/usr/bin/env python3
"""v2 figure library: SVG (settled) + manifest + GSAP fragment for every figure slide.

Contract: deck-animation skill. Base SVG = settled state, element ids slide-scoped
(fs<slide key>-...), fragment = paused timeline, first record is the TOTAL spacer,
every animated parameter written fromTo, no loops, no wall clock.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "assets"))

W_A, H_A = 800, 900          # content-left figure zone (672x755 at the embed)
W_B, H_B = 1600, 640         # diagram layout zone (1728x~687 at the embed)

BG = "#2b1b3d"
SURF = "#3d2554"
LINE = "#6b4a8a"
TXT = "#fdf3e7"
MUT = "#cbbcd6"
OR = "#ff6b35"
ROSE = "#ff2e88"
FONT = "Montserrat, 'Century Gothic', sans-serif"

DIM = 0.16   # opacity of an element that has not had its beat yet


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def T(x, y, s, size=26, fill=TXT, anchor="middle", weight=400, gid=None, ls=None):
    ida = f' id="{gid}"' if gid else ""
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text{ida} x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{lsa}>{esc(s)}</text>')


def R(x, y, w, h, rx=14, fill=SURF, stroke=LINE, sw=2, gid=None, dash=None,
      opa=None, sid=None):
    ida = f' id="{gid}"' if gid else ""
    das = f' stroke-dasharray="{dash}"' if dash else ""
    op = f' opacity="{opa}"' if opa is not None else ""
    return (f'<rect{ida} x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{das}{op}/>')


def lines_box(x, y, w, h, lines, size=26, fill=TXT, gid=None, stroke=LINE,
              rx=16, weight=400, lh=1.32, fills=None, top=None):
    """Rounded box with vertically centered lines of text."""
    n = len(lines)
    step = size * lh
    if top is None:
        top = y + h / 2 - (n - 1) * step / 2 + size * 0.34
    out = [R(x, y, w, h, rx=rx, stroke=stroke, gid=gid)]
    for i, ln in enumerate(lines):
        f = fills[i] if fills else fill
        wgt = weight[i] if isinstance(weight, list) else weight
        out.append(T(x + w / 2, top + i * step, ln, size=size, fill=f, weight=wgt))
    return "".join(out)


def pill(x, y, w, h, label, size=26, fill=ROSE, txt=BG, stroke=None, gid=None,
         weight=700):
    st = stroke or fill
    return (R(x, y, w, h, rx=h / 2, fill=fill, stroke=st, sw=2, gid=gid)
            + T(x + w / 2, y + h / 2 + size * 0.34, label, size=size, fill=txt,
                weight=weight))


def arrow(pts, aid, color=LINE, sw=3.5, hl=18, hw=15):
    d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
    shaft = (f'<path id="{aid}" d="{d}" fill="none" stroke="{color}" '
             f'stroke-width="{sw}" pathLength="100" stroke-dasharray="100" '
             f'stroke-dashoffset="0" stroke-linecap="round" '
             f'stroke-linejoin="round"/>')
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    ln = math.hypot(x2 - x1, y2 - y1) or 1.0
    ux, uy = (x2 - x1) / ln, (y2 - y1) / ln
    px, py = -uy, ux
    p1 = (x2 - hl * ux + hw / 2 * px, y2 - hl * uy + hw / 2 * py)
    p2 = (x2 - hl * ux - hw / 2 * px, y2 - hl * uy - hw / 2 * py)
    head = (f'<path id="{aid}h" d="M {x2},{y2} L {p1[0]:.1f},{p1[1]:.1f} '
            f'L {p2[0]:.1f},{p2[1]:.1f} Z" fill="{color}"/>')
    return shaft + head


def draw(pid, pts, color, sw=9, closed=False):
    d = "M " + " L ".join(f"{x},{y}" for x, y in pts) + (" Z" if closed else "")
    return (f'<path id="{pid}" d="{d}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" pathLength="100" stroke-dasharray="100" '
            f'stroke-dashoffset="0" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


def chip(x, y, w, h, lines, size=24, fill=SURF, stroke=LINE, gid=None,
         color=TXT, weight=400):
    if isinstance(lines, str):
        lines = [lines]
    n = len(lines)
    step = size * 1.28
    top = y + h / 2 - (n - 1) * step / 2 + size * 0.34
    out = [R(x, y, w, h, rx=10, fill=fill, stroke=stroke, sw=1.6, gid=gid)]
    for i, ln in enumerate(lines):
        out.append(T(x + w / 2, top + i * step, ln, size=size, fill=color,
                     weight=weight))
    return "".join(out)


# --------------------------------------------------------------------------
# figure factory
# --------------------------------------------------------------------------
FIGS = []


def figure(key, vb, fn, dur, beats, notes):
    W, H = vb
    body, tw, els = fn()
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" font-family="{FONT}">\n'
           f'<rect x="0" y="0" width="{W}" height="{H}" fill="{BG}"/>\n'
           f'<g id="f{key}-all">\n{body}\n</g>\n</svg>\n')
    FIGS.append(dict(key=key, svg=svg, W=W, H=H, dur=dur, beats=beats,
                     tweens=tw, els=els, notes=notes))


def tl_js(fig):
    out = ["window.FigTl = (gsap) => {",
           "  const tl = gsap.timeline({ paused: true });",
           f'  const TOTAL = {fig["dur"]};',
           "  tl.set({}, {}, TOTAL);"]
    heads = []
    for t in fig["tweens"]:
        sel, kind, pos, d = t["sel"], t["kind"], t["t"], t["d"]
        if kind == "wrap":
            out.append(f'  tl.fromTo("{sel}", {{ autoAlpha: 0 }}, '
                       f'{{ autoAlpha: 1, duration: {d}, ease: "none" }}, {pos});')
        elif kind == "rise":
            to = t.get("to", 1)
            out.append(f'  tl.fromTo("{sel}", {{ autoAlpha: {DIM} }}, '
                       f'{{ autoAlpha: {to}, duration: {d}, ease: "none" }}, {pos});')
        elif kind == "sink":
            to = t.get("to", 0.28)
            out.append(f'  tl.fromTo("{sel}", {{ autoAlpha: 1 }}, '
                       f'{{ autoAlpha: {to}, duration: {d}, ease: "none" }}, {pos});')
        elif kind == "draw":
            out.append(f'  tl.fromTo("{sel}", {{ strokeDashoffset: 100 }}, '
                       f'{{ strokeDashoffset: 0, duration: {d}, ease: "none" }}, {pos});')
            heads.append((sel + "h", pos + d * 0.72, 0.12 if d < 1 else 0.18))
        elif kind == "head":
            heads.append((sel, pos, d))
        elif kind == "grow":
            out.append(f'  tl.fromTo("{sel}", {{ scaleX: 0, transformOrigin: "0% 50%" }}, '
                       f'{{ scaleX: 1, duration: {d}, ease: "none" }}, {pos});')
        else:
            raise SystemExit("unknown tween kind " + kind)
    for sel, pos, d in heads:
        out.append(f'  tl.set("{sel}", {{ autoAlpha: 0 }}, 0);')
        out.append(f'  tl.to("{sel}", {{ autoAlpha: 1, duration: {d} }}, {pos});')
    out += ["  return tl;", "};", ""]
    return "\n".join(out)


def manifest(fig):
    return {
        "id": fig["key"],
        "duration": fig["dur"],
        "viewBox": f'0 0 {fig["W"]} {fig["H"]}',
        "beats": [{"id": b[0], "t0": b[1], "t1": b[2]} for b in fig["beats"]],
        "elements": [{"id": e[0], "beat": e[1], "role": e[2], "state0": e[3]}
                     for e in fig["els"]],
        "notes": fig["notes"],
    }


SPEED = 0.85   # global compression of the within-beat choreography


def beat_index(beats, t):
    for i, b in enumerate(beats[:-1]):
        if b[1] - 1e-6 <= t < b[2] - 1e-6:
            return i
    return len(beats) - 1


def normalize(fig):
    """Derive the beat windows from the tween distribution.

    A pose is only true at a beat centre if every tween of that beat finished
    before it: window = 2 * (action length) + margin (T-3).
    """
    beats = fig["beats"]
    groups = {i: [] for i in range(len(beats))}
    for t in fig["tweens"]:
        groups[beat_index(beats, t["t"])].append(t)
    new = []
    for i, (bid, t0_old, _t1_old) in enumerate(beats):
        g = groups[i]
        for t in g:
            t["r"] = (t["t"] - t0_old) * (SPEED if i else 1.0)
            if i:
                t["d"] = round(t["d"] * SPEED, 3)
        act = max([t["r"] + t["d"] for t in g], default=0.0)
        if i == 0:
            start, end = 0.0, max(0.9, 2 * act + 0.05)
        else:
            start = new[-1][2] + 0.05
            end = start + 2 * act + 0.12
        for t in g:
            t["t"] = round(start + t["r"], 3)
            t.pop("r", None)
        new.append([bid, round(start, 3), round(end, 3)])
    new[-1][2] = round(new[-1][2] + 0.45, 3)   # settled hold
    fig["beats"] = [tuple(b) for b in new]
    fig["dur"] = round(new[-1][2], 2)


def beat_containing(fig, t):
    """Half-open windows: a tween at the beat boundary belongs to the next beat."""
    beats = fig["beats"]
    for b in beats[:-1]:
        if b[1] - 1e-6 <= t < b[2] - 1e-6:
            return b
    return beats[-1]


def check_timing(fig):
    """Every tween must be finished by the centre of its beat (T-3)."""
    bad = []
    for t in fig["tweens"]:
        b = beat_containing(fig, t["t"])
        centre = (b[1] + b[2]) / 2
        end = t["t"] + t["d"]
        if t["kind"] == "draw":
            # the arrowhead fades in at 0.72 d for 0.12 s
            end = max(end, t["t"] + 0.72 * t["d"] + 0.12)
        if end > centre + 0.02:
            bad.append("%s %s t=%.2f d=%.2f end=%.2f > centre %.2f (beat %s)"
                       % (fig["key"], t["sel"], t["t"], t["d"], end, centre, b[0]))
    return bad


def write_all():
    os.makedirs(OUT, exist_ok=True)
    for f in FIGS:
        normalize(f)
    for f in FIGS:
        open(os.path.join(OUT, f"fig-{f['key']}.svg"), "w",
             encoding="utf-8").write(f["svg"])
        open(os.path.join(OUT, f"fig-{f['key']}.tl.js"), "w",
             encoding="utf-8").write(tl_js(f))
        open(os.path.join(OUT, f"fig-{f['key']}.manifest.json"), "w",
             encoding="utf-8").write(json.dumps(manifest(f), ensure_ascii=False,
                                                indent=1) + "\n")
    print(f"wrote {len(FIGS)} figure sets to {OUT}")
    problems = []
    for f in FIGS:
        problems += check_timing(f)
    if problems:
        print("TIMING VIOLATIONS (%d):" % len(problems))
        for p in problems:
            print("  -", p)
    else:
        print("timing OK: every tween ends before its beat centre")


