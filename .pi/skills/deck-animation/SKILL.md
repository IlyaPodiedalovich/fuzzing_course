---
name: deck-animation
description: "Use this skill to turn a drawable presentation figure (kind diagram / chart / circuit) from a presentation skeleton into presentation-ready figure assets: a settled-state SVG with semantic element ids, an element/beat manifest, a paused GSAP timeline fragment (D2), and a settled PNG raster. Invoked by the deck skills (deck-pptx embeds the PNG; deck-html embeds the SVG + fragment) — not a standalone user step. Out of scope: text animation (owned by the deck skills), slide assembly, deck-level loops. Trigger whenever a skeleton figure must be drawn or re-drawn for a deck, or when figure assets (fig-<id>.svg / .tl.js / .png) are missing or wrong."
---

# Deck animation — figure assets (SVG + manifest + GSAP fragment + PNG)

One figure, four deliverables. The skill produces the animation **to be added to a
slide**; integrating it into the slide is the deck skill's job.

| File | What it is |
|---|---|
| `fig-<id>.svg` | the **settled state** (final picture), line art, opaque figfill background, **semantic ids on every beat-relevant element** |
| `fig-<id>.manifest.json` | duration, per-beat timing, element list (`id`, beat, role, `state0`) |
| `fig-<id>.tl.js` | **paused** GSAP timeline fragment for the figure only (D2) |
| `fig-<id>.png` | settled state rasterized (for the PPTX target) |

## Input contract (supplied by the invoking deck skill)

- the figure object from the skeleton: `kind`, `prompt`, `caption`
- the slide's anim beat table: `beats` (id / pose / change / accent), `settled`, `duration`
- `meta.anim_role` (`factual` / `entertaining` / `mixed`)
- design tokens: palette (`bg`, `body`, `accent`, `figfill`, `figline`, `figtext`), font
  stack, any DS factura note for the figure's static look
- the figure zone aspect (embed target) — pick the canvas close to it (~1600px wide);
  the deck letterboxes the rest onto the figfill panel

Only the figure-relevant beat poses matter; text-column beats are out of scope here.

## Workflow

1. **Read** figure + beat table + `settled` + tokens + zone aspect. When
   `anim_role` is `factual`, every element you draw must be factually true — the figure
   is part of the explanation, not decoration. Re-check the physics/electronics/circuit
   facts before drawing.
2. **Element list.** Give every beat-relevant element a semantic id — and ids are
   **SLIDE-SCOPED**: prefix them with the figure's slide key (the real-report
   convention: slide `s5` → `fs5-branch`, `fs5-node-a`; `s9` → `fs9-…`). Several
   figures inline into one `deck.html` and SVG ids / GSAP selectors are
   document-global — two figures sharing an element id break cross-slide
   selectors and `getElementById`; deck-html's assembler FAILs the build on
   duplicate figure element ids. Decide the per-beat timing: distribute the
   beats across `duration` (creative, but record it) — first beat is the cold
   base, the settled pose holds until the end. **Appearance budget:** for
   `anim_role: entertaining` the figure must be fully settled within 2 s of
   slide activation — the manifest `duration` total is checked against that
   budget (the text wave may run alongside; the budget is on the figure).
3. **Draw the SVG** (see `references/figure-methodology.md`): base geometry = the
   **settled state** (print contract — with JS off the picture must be the final one);
   layers `base` / `state-*` (default visibility = settled visibility) / `flow-el`
   (live-only, hidden in print); palette from tokens (strokes `figline`, labels
   `figtext`/`body`, `accent` reserved for informative highlights — if a beat needs
   two opposed states, use accent + a neutral (body) contrast and note it); static
   rules —
   clearance (T-12), no text on the plot (T-15), label size at the embed (T-16),
   state readability (T-6), plain text for subscripts (no Unicode subscript chars).
4. **Write the manifest** (`fig-<id>.manifest.json`):
   `{ "id", "duration", "viewBox": "0 0 W H", "beats": [{id, t0, t1}], "elements":
   [{id, beat, role, state0}], "notes" }` (`state0` ∈ {visible, hidden, undrawn,
   dimmed}; a short free string is fine for anything else).
5. **Write the fragment** (`fig-<id>.tl.js`) — D2, exact contract:
   ```js
   window.FigTl = (gsap) => {
     const tl = gsap.timeline({ paused: true });
     const TOTAL = <manifest.duration>;
     tl.set({}, {}, TOTAL);                 // duration spacer — FIRST tween (T-5)
     tl.fromTo("#flat-branch", { strokeDashoffset: 100 },
               { strokeDashoffset: 0, duration: 1.4, ease: "none" }, 0.8); // b1
     /* …one block per beat… */
     return tl;
   };
   ```
   Rules: every animated parameter written `fromTo` (safe for forward and backward
   seeks); no tween past TOTAL; continuous motion as FINITE tweens
   (never `repeat: -1`); no `setTimeout` / `Math.random` / `Date.now`; curve draw =
   `pathLength="100"` + `stroke-dashoffset 100→0` (C1b, T-7/T-9/T-10); never combine
   `autoAlpha` with dash properties in one tween (T-9); moving dots =
   `getPointAtLength` in `onUpdate` (M3b); decorative flow dashes carry
   `class="flow-el"` and must contrast the base path (~89 px/s, T-13). The fragment
   never loops itself — the deck-level slide loop (T-14), where the deck runs the
   loop-capable runtime (the loop policy, the deck-html skill), restarts the whole
   slide timeline.
6. **Rasterize** the settled PNG: `scripts/svg2png.sh fig-<id>.svg fig-<id>.png`.
7. **QA loop** (this skill's own — repeat until clean):
   1. `scripts/fig_harness.py fig-<id>.svg fig-<id>.tl.js fig-<id>.manifest.json
      <outdir>` → self-contained capture page (pinned `?t=` fraction, no loop).
   2. `scripts/capture.sh <outdir>/harness.html fig-<id>.manifest.json <frames dir>`
      → keyframes at every beat center + cold + settled, blank-frame check, R3
      double-render (md5 must match).
   3. Inspect the frames **at full resolution** (chat previews ghost at 96 dpi): each
      beat center matches the beat table pose; clearance holds in every frame state;
      the settled frame carries the complete fact.
   4. Optional: the `hyperframes` CLI (v0.8.162 pinned) needs a composition root and a
      browser session — a bare harness dir fails in a headless-only environment. If it
      runs: `hf check` (whitelist `Math.random`/`Date.now` inside vendored
      `gsap.min.js` — false positives) + `hf keyframes`; record the output in notes.
      Otherwise record and skip.
   5. Broken state found → copy it to `archive/` in the run dir **before** fixing in
      place (AGENTS.md rule). Fix the SVG / manifest / fragment — never hand-edit the
      PNG — and re-run the capture.
8. **Deliver**: the four files (plus the harness/frames under the run dir) and a short
   note on any residual defect for the deck skill to report to the user.

## Scripts

Paths relative to this skill's directory.

| Script | What it does |
|---|---|
| `scripts/fig_harness.py <fig.svg> <fig.tl.js> <manifest.json> <outdir>` | builds `outdir/harness.html` — the figure inlined with the vendored GSAP and the fragment; `?t=<0..1>` pins `tl.progress` (deterministic capture) |
| `scripts/capture.sh <harness.html> <manifest.json> <outdir> [WxH]` | `node --check` on the fragment; keyframes at each beat center + cold + settled; blank-frame guard; R3 double-render md5 (fails the script on mismatch) |
| `scripts/svg2png.sh <in.svg> <out.png> [WxH]` | chromium headless rasterize at the SVG viewBox size |

## Integration contract (for the deck skills)

- **deck-pptx**: embeds `fig-<id>.png` via the per-slide `figure_images` tokens mapping;
  the fragment and manifest are not used on that target.
- **deck-html**: inlines `fig-<id>.svg` into the slide; adds the fragment to the slide
  timeline (`slideTl.add(FigTl(gsap), offset)`; scale with `timeScale` if the slide
  duration differs from the manifest); owns the slide loop (T-14, on loop decks) and
  the print CSS that hides `.flow-el`.

## Gotchas

- The base SVG must be the settled state, not an empty canvas — print/PDF shows the
  SVG as-is when the timeline never ran (T-1).
- Every draw path needs `pathLength="100"`; a 0..1 dash range quantizes to a step
  function in headless capture (T-7).
- `repeat: -1` anywhere in the fragment makes the duration a sentinel and all mid
  frames collapse to the end state (T-5) — use finite tweens over the window.
- Element entry: a tiny `autoAlpha` set **separate** from the dash tween (T-9).
- Captions are not baked into the SVG — the deck skill places the skeleton's
  `caption` in HTML; the SVG contains the figure only.
- Subscripts: plain text («U вых», «I_s») — Unicode subscript glyphs are mostly tofu.
- Work in the run dir's `assets/` (or `figures/<id>/`); never modify the skeleton or
  the fixture to fix a rendering problem.
