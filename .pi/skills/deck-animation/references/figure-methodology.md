# Figure methodology (ticket-13 frozen rules, figure scope)

How to go from a skeleton figure (`prompt` + beat table + `settled`) to a correct
`fig-<id>.svg` + `fig-<id>.tl.js`. Text animation is out of scope here — this is the
figure's own picture and motion.

## 0. Stack (frozen)

- Carriers: the figure is **inline SVG**. No canvas/Lottie/video.
- Engine: GSAP (the deck skill vendors it); ONE **paused timeline per figure**
  (`fig-<id>.tl.js`), exposed as `window.FigTl(gsap)`. The deck skill adds it to the
  slide timeline.
- Determinism (R3): the rendered frame is a pure function of t. No wall clock, no
  `Math.random`, no async state after load. Write every animated parameter with
  `fromTo` (safe for forward and backward seeks). Continuous motion uses **finite**
  tweens that map deterministically under `tl.progress` (T-5).

## 1. Procedure

### Step 1 — state decomposition
List the stable visual states the audience must see as pictures. Each state = element
properties: visibility, color, position, path draw progress, labels. A state is a pose,
not a process. Use the skeleton's beat table: keep only the figure-relevant poses
(text-column states are ignored).

### Step 2 — beat timing
Distribute the beats across `duration` (creative; record the result in the
manifest). Appearance budget: the rule and its check live in SKILL.md step 2
(entertaining figures settle within 2 s of activation — the `duration` total
is what it is checked against):
- first beat = cold base (≈ 0.4–0.8 s): the base rises in;
- informative beats in the middle — each changes only its listed properties, all else
  holds;
- last beat = **settled**: the final picture holds until `TOTAL` (the loop, if any,
  restarts the slide timeline — T-14 — the fragment itself never repeats).
Review ("mid") frames are the beat centers, never blindly t=0.5 (T-3). Place the
tweens so each beat's END state is reached by the beat's CENTER — the review frame
at the center must show the beat's complete pose (a draw finishing at or after the
center reads as half-drawn).

### Step 3 — SVG plan
- Base geometry = the **SETTLED state**. Print contract: with JavaScript off (or in
  `@media print`) the picture must already be the final one (T-1). Animations are
  deviations from the base, written `fromTo`.
- Semantic ids on every beat-relevant element.
- Layers:
  - `base`: wires, nodes, component bodies, static labels, direction arrows — always
    visible, drawn as in the settled state;
  - `state-*`: state overlays (region highlights, paths, points, insets, notes) —
    default visibility = their settled visibility (visible for the final state, hidden
    for earlier-only states);
  - `flow-el`: decorative live motion only (moving dashes) — hidden in print by the
    deck's print CSS. **Direction is encoded geometrically** (static arrows in `base`);
    flow motion is decorative.
- Cold-frame convention: at t=0 the base may still be hidden (the b0 `fromTo`
  autoAlpha rises it in) — that is the cold state, not a defect; the settled frame
  must be complete.
- Canvas: ~1600px wide, aspect close to the embed zone; opaque `figfill` background
  rect; palette from tokens (strokes `figline`, labels `figtext`/`body`, one `accent`).
- The caption is NOT drawn into the SVG — the deck skill places the skeleton's
  `caption` in HTML; the SVG contains the figure only.
- `factual` role: every element is factually true.

### Step 4 — the fragment
`gsap.timeline({ paused: true })`; `tl.set({}, {}, TOTAL)` FIRST (T-5 spacer, no tween
past TOTAL); one block per beat at its `t0`. Mechanism catalog:

| Type | Mechanism | Notes |
|---|---|---|
| State layer appears | M1 `fromTo` `autoAlpha` (0.3–0.5 s) | determinism by structure; separate from any dash tween (T-9) |
| Live attribute (color, position) | M2 `fromTo` on the attribute | fewer nodes than pre-rendered layers |
| Curve / path draw | C1b `stroke-dashoffset` + `pathLength="100"`, tween `100 → 0` | STANDARD (T-7); reveal visibility with a separate tiny autoAlpha tween (T-9); DrawSVG rejected (T-10) |
| Moving dot along a path | M3b `getPointAtLength` in `onUpdate`, pure function of progress | STANDARD, no plugin |
| Flow (decorative current) | M4 moving dashes, `ease: "none"`, finite over the window | must contrast the base path (white on accent), ~89 px/s (T-13) |
| Live value text | C3 `onUpdate` → `textContent = f(self.progress())` | never read wall time |

### Step 5 — QA protocol (per figure)
- Harness: `scripts/fig_harness.py`; frames: `scripts/capture.sh` — cold, every beat
  center, settled.
- Frames judged at full resolution: pose matches the beat table; clearance in every
  frame state (T-12); settled frame = the complete fact (T-6).
- R3: the first informative beat center and t=1 rendered twice → md5-identical.
- Circuit figures: trace every marked current path end-to-end (source → device →
  load → device → source) — the path line must pass through the load; draw paths
  under the components so the components stay readable.
- Optional: `hf check` (whitelist vendored GSAP) + `hf keyframes` table.
- Broken frames → `archive/` before the in-place fix.

## 2. Rules (frozen from ticket 13 + reviews)

- **T-5 (P0):** `tl.set({}, {}, TOTAL)` pins the duration; prefer finite tweens for
  continuous motion (one linear tween over the window instead of `repeat: -1`). A
  mid-frame identical to the settled frame means the seek mapping is broken — re-check
  the duration before reviewing.
- **T-6 (design):** an element's STATE must stay readable when a path or highlight
  overlays it. Keep state markers independent: contact/pivot dots above the path, the
  element label accented in the active state. A straight overlay is not enough to read
  a state change.
- **T-7 (P0):** scale draw paths to `pathLength="100"`, `stroke-dasharray: 100`, tween
  `100 → 0`. Unitless/short-range dash values quantize to a step function in headless
  capture.
- **T-9 (P0):** never combine `autoAlpha`/`visibility` with a dash property in the SAME
  tween on an SVG element — headless capture then shows a stale dash raster. Structure:
  `tl.set(el, { autoAlpha: 0 }, pos); tl.to(el, { autoAlpha: 1, duration: .01 }, pos);`
  plus a dash-only `fromTo` at the same position.
- **T-10:** DrawSVGPlugin is incompatible with deterministic `?t=` capture (pixel state
  lags the DOM). Dropped; C1b is the standard.
- **T-12 (design):** CLEARANCE — text keeps a visible clearance from every visual
  element it does not belong to (label vs element, label vs label, note vs curve,
  caption vs body). Non-overlap is not enough; clearance must hold in EVERY frame
  state (t=0, mids, settled). Judge by eye on the frames; when a label is too close to
  a foreign element, move the LABEL into an open zone — never shrink the diagram.
- **T-13 (design):** M4 moving dashes that share the base path's color read as static
  arrows. Flow dashes contrast (white on the accent) and move ~89 px/s (40 px per
  0.45 s). The standard current indicator is the M3b moving dot; M4 is a decorative
  accent.
- **T-14 (deck-level, for reference):** text slides never loop (any role); figure
  slides replay only on LOOP DECKS — where the user's stated policy selects the
  loop-capable runtime (the loop policy, the deck-html skill): play → hold settled
  1.5 s → restart, implemented outside the timeline (`onComplete` + `setTimeout` +
  `restart()`), never `tl.repeat`. The fragment therefore stays loop-free (it is
  loop-free even on loop decks — the loop is deck-level).
- **T-15 (design):** text never sits ON the plot — no label crosses a curve, an axis
  line, a tick column, or another label's zone; leader lines may touch their target
  but must not cross the curve or text. Move text into open zones, never shrink the
  diagram.
- **T-16 (design):** legibility at EMBED size — labels are sized to the embed zone,
  not the 1:1 canvas: side zone (≈660×790) — every figure text ≥ 20 px; full-slide
  figure (≈1700 px wide) — ≥ 25 px (the full-slide bar is the body floor). If the
  prompt's content does not fit at that size → cut the number of elements, or
  flag the invoking deck skill to consider layout `diagram`.
- **Subscripts:** Unicode subscript glyphs exist only for a e o x ɛ h k l m n p s t —
  other letters are tofu. Use plain text («U вых», «I_s», «C_j»).

## 3. Static-diagram quality bar (applies to the settled PNG too)

The settled frame is what the PPTX target embeds and what print shows — it is the
diagram, judged as a static illustration: complete fact (T-6), clearance (T-12),
plot-overlap (T-15), one informative accent, line art from the token palette, legible
at the embed size (assume the figure zone, not 1:1).
