# Animation methodology (D2, deck-html side)

Runtime: **GSAP D2 only** (vendored `lib/gsap.min.js`, inlined). No CSS-animation
content motion (A1/D1 excluded by decision), no scroll-driven effects, no interactive
elements (keyboard navigation only).

## Per-slide timelines

- One **paused** timeline per slide, built lazily on first show. All animated
  parameters written `fromTo` (safe for forward and backward seeks).
- T-5: the timeline starts with a TOTAL spacer (`tl.set({}, {}, TOTAL)`) and no tween
  may run past TOTAL — the settled state is a real, seekable end.
- Slide timeline = text wave first, then the figure timeline added at a start offset
  (see Figure integration). The slide total = the later of the two.
- **R3**: two headless captures of the same `?slide=N&t=X` (progress) with the same
  `--virtual-time-budget` must be **md5-identical** (render_html.sh probes this).
  No random, no Date.now in generated code (the vendored GSAP contains both —
  whitelisted, never called by the generated code).

## Text reveal (all roles)

A compact block wave: each `.reveal` element (title, li, card, formula, table group)
`fromTo` opacity 0→1, y 28→0, 0.5 s `power2.out`, stagger 0.10, in DOM order (title
first). Bounds (T-11): no rotation/scale on text, max y-offset 30, the wave stays ≲ 1 s
(the skeleton's description already keeps text compact — text carries no meaning).
**Text slides never loop** (any role — the description has no loop to describe; the
runtime enforces it).

## anim_role — the deck-html interpretation

The axis (informational weight of motion) is SET by the skeleton
(`references/animation-scripting.md` in presentation-skeleton): factual /
entertaining / mixed. This skill interprets it:

- **factual** — the figure's beat table is the source of truth; every pose true
  (enforced at draw time by deck-animation); **no loops at all** (the loop-capable
  runtime must not be selected for a factual deck); the PDF must be readable as a
  static printout (settled picture carries the complete fact).
- **entertaining** — motion may carry atmosphere; loops allowed only under the
  loop policy (SKILL.md): the user's stated policy must ask for them AND the
  loop-capable runtime must be explicitly selected — the role never implies a
  loop by itself; figure content stays correct — the role changes the style of
  motion, never the truth of what is drawn.
- **mixed** — per slide: figure slides follow the factual rules; text/title slides
  may use the entertaining style (text slides still never loop).

The role is a **gate on what the figure fragment may contain** — it is not a
knob on the text reveal, and it is NOT the loop decision (the loop policy,
SKILL.md, owns that).

## Figure integration (assets from deck-animation)

Per-figure asset set: `fig-<id>.svg` (settled, semantic ids), `fig-<id>.manifest.json`,
`fig-<id>.tl.js` (paused fragment: `window.FigTl = (gsap) => { … }`), `fig-<id>.png`
(settled raster — PPTX target; not used by this target).

- The **settled SVG is inlined** into the figure zone. Its base geometry IS the
  settled state → with JS off (print, no-GSAP) the picture is already the final one.
  This is what makes the PDF print-safe by construction (F-P2).
- The fragment is inlined per figure with a wrapper — multiple figures in one deck
  must not collide on `window.FigTl`:
  ```js
  FIGS["s4"] = (function(){ <fig-s4.tl.js content>; return window.FigTl; })();
  ```
  (captured immediately, per file).
- Slide wiring: the text wave plays; the figure timeline (its own seconds, from the
  manifest `duration`) is added at a start offset (after the title reveal); the slide
  total grows to cover it.
- **Loop (T-14)** — loop decks only: the T-14 wiring exists only in the
  loop-capable runtime (`runtime.js`); the default `runtime-noloop.js` has no
  such wiring at all, so on the default runtime there is nothing to loop
  (slide activation is the only trigger). When selected: figure slides only,
  deck-level restart, NOT `tl.repeat`: `onComplete → setTimeout(1500 ms
  hold) → progress(0).play()` — and only while the slide is still active.
  Disabled in capture mode (`?t=`) and in print (the print guard kills timers
  and seeks every timeline to its end).
- `.flow-el` (decorative live dashes): hidden by print CSS; on screen they move only
  while the slide is active.
- Figure-static rules (from deck-animation, still binding in review): T-12 clearance
  (move the label, never shrink the diagram — holds in every frame), T-15 no text on
  the plot, T-6 state readability in every beat.

## Frame protocol (review)

Per slide: `t=0` (cold base), `t=1` (settled — the main review frame), and for figure
slides a mid frame at the first informative **beat center** (T-3 — never blindly
t=0.5). Plus the **PDF page** (print freeze: settled figures, no `.flow-el`, text
visible). Review at full resolution (96-dpi previews ghost — F-H1).

Naming: frame files and `?slide=` use the slide POSITION (1-based), not the
skeleton id. `render_html.sh` auto-captures the mid frame at `t=0.5` (mechanical
default) — check it against the beat table; when the first informative beat is not
near 0.5, capture the mid manually with `?t=`.

## Runtime URL parameters (capture / gate / debug)

- `?slide=N&t=X` — capture mode: seek slide N (1-based position) to progress X
  and freeze (R3 determinism; the print guard also freezes on print).
- `?audit=1` — the layout gate (F-H3, `scripts/text_audit.py`): every slide is
  forced to its settled pose, then every settled-VISIBLE leaf text rect is
  measured — OVERFLOW (outside the 1920×1080 stage) and OVERLAP (two non-nested
  leaves intersect by more than 4 px in both dimensions, > 120 px² — border
  grazing is not a collision). Elements invisible at settle (inline
  `visibility:hidden` — GSAP autoAlpha / base-SVG state groups — or opacity 0)
  are excluded; slide-stack hiddenness is not (stacked slides keep a valid
  layout and are audited too). Intentional overlay text (badge, page number)
  opts out with `data-ov`. Results: `<pre id="audit-out">` + console.
- `?probe=sel1,sel2` — geometry diagnostics for named selectors (prints
  `[left,top right,bottom]` per selector; MISSING when absent).

## Print freeze (the contract)

- CSS: `@media print { .reveal { opacity: 1 !important; transform: none !important }
  .flow-el { display: none !important } }` — the settled text state is guaranteed by
  CSS, independent of runtime.
- SVG: base geometry = settled (deck-animation contract) — guaranteed by the asset.
- Runtime: on `beforeprint` / print media — pause every timeline at its end, kill loop
  timers. The PDF must match the settled screen state, page by page.
