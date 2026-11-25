# Gotchas (accumulated findings)

## Print / PDF

- **F-P1** — without `@page { size: 1920px 1080px; margin: 0 }` Chromium prints Letter
  pages and clips every slide at the right edge. Gate: pdfinfo `Page size: 1440 x 810
  pts` + `Pages == N`.
- **F-P2** — a D2 deck printed before its timelines reached the end produces a blank
  or half-drawn PDF. The settled state must come from CSS (`.reveal !important`) +
  the authored SVG base, never from runtime timeline state. The runtime's print guard
  (seek to end + kill timers) is a second line, not the contract.

## Rendering / review

- **F-H1** — 96-dpi chat previews ghost and smear thin strokes. Review at full
  resolution; low-res "defects" are often compression artifacts (verified twice:
  s7 bridge paths, s4 ticks).
- **F-H2** — invalid XML entities in inlined SVG (`&asymp;`, `&ge;`, …) make Chromium
  show an error banner inside the rasterized/inline SVG. Only the five XML entities
  (`&amp; &lt; &gt; &quot; &apos;`) or numeric refs (`&#8776;`).
- **F-H3** — an unclosed `</svg>` is tolerated by the animation harness (GSAP still
  drives it) but breaks bare rasterization and inline embedding. Write closed SVGs;
  the capture step is the detector.
- **F-H4** — an element that belongs only to a mid-beat state must be explicitly
  hidden in the settled base, not left visible: the base geometry is the SETTLED
  state (the E_g lesson: a mark in a flat-band group was absent at settle).
- **F-H5** — the screen render can be broken while every gate is green. The
  mechanism (real-report build-issues #4): an effects rule
  `section.slide{position:relative}` (specificity (0,1,1)) overriding the vendor
  `.slide{position:absolute;inset:0}` (0,1,0) for a pseudo-element positioning
  context. Slides then lay in normal flow in a stack (each 1080 px down); the
  stage's `overflow:hidden` shows only the first — every non-first settled frame
  is uniform background. content_check reads DOM text, r3 proves byte-stability
  (a uniform frame is stable), pdf-* sees the print render, which is a separate
  (correct) pipeline. Gate: `GATE visible-content` — every `s<i>-t1.png` must carry
  content (grayscale stddev ≥ 0.01, ImageMagick, `render_html.sh`). Rule: **effects CSS must not
  touch the `position` of `.slide` or `.inner`** (`.inner{position:relative}` is
  the sibling bug: `inset` is ignored and the box collapses to content height).
  A textured (non-solid) slide background raises the uniform baseline — raise
  `STDDEV_MIN` with it.

## Theming

- **T-D1** — theme keys use underscores (`slide_bg`), the CSS vars must be emitted
  hyphenated (`--slide-bg`): the vendor base and the content template read the
  hyphenated names and fall back when they miss (`var(--slide-bg, #fff)` → the whole
  deck renders on WHITE with ~1.3:1 text contrast; the dark figure panels still
  resolve because single-word vars like `--figfill` match). `token_css` does the
  mapping (`k.replace('_','-')`). Verify a theme run with a pixel sample of the slide
  background, not by eye at montage scale — the white-slide defect survived two
  visual reviews before an agent caught it (low-res tiles + dark panels masked it).
- **S-1-bug** — a token map string must live inside a selector (e.g. `:root{…}`);
  a top-level `--x:…` line outside any selector breaks the whole stylesheet.
- **S-2** — wide/landscape figures need the full-width zone (diagram layout, or
  full-with-figure-below), not the 720×843 side zone; letterboxing a 1600×440 asset
  into the side zone leaves near-empty strips.
- **S-3** — dense text: split the slide or trim the wording. The skeleton and the
  generator never shrink fonts.
- **S-4** — font subsets: without a cyrillic subset, RU text falls back to a different
  font mid-sentence (metric drift). Check coverage before freezing a theme package.

## Capture / determinism

- **C-1** — capture flags are the contract: `--headless=new --force-device-scale-factor=1
  --window-size=1920,1080 --hide-scrollbars --virtual-time-budget=<ms>` + the URL
  `?slide=N&t=progress` (`?capture=1` pins the stage 1:1). The `t-pinned` class kills
  CSS transitions during pinned seeks.
- **C-2** — R3 compares two runs with the SAME budget; a budget below the slide total
  (9 s default) freezes mid-tween and "differences" appear.
- **C-3** — PDF gate values: 1920×1080 px = 1440×810 pt at 96 dpi; `--no-pdf-header-footer`
  is required or the pages shift down.
- **C-4** — CSS transitions stall at time 0 under headless chromium with
  `--virtual-time-budget`: an opacity 0→1 transition started on load was still
  `CSSTransition: running, currentTime 0` 13 s later (verified by getAnimations probe),
  so the slide stayed invisible in every live-mode (`?slide=N` without `t`) capture.
  `t-pinned` only kills transitions in `?t=` capture mode. Rule: the generated deck
  carries **zero CSS transitions** — slides appear instantly, ALL motion is GSAP
  (seekable, R3-stable, capture-safe). If a future effect needs a transition, it must
  also be replicated in the GSAP wave.

## Generation

- **G-1** — the `<section>` class attribute is built by concatenating conditional
  fragments (`title-2`, `has-fig`); the closing quote must come
  AFTER all fragments. A misplaced quote silently produces bare boolean attributes
  (`…" title-2` → `title-2` outside the class → layout rules never
  apply, and text-based checks still pass). Gate: content_check.py rejects any
  section tag that does not fullmatch `deck_common.SECTION_RE` —
  `<section class="slide [a-z0-9-]+( [a-z0-9-]+)*" id="…">` (one source for gate,
  assembler and generator). The old `data-loop="1"` attribute is retired
  (the loop policy: loop presence is a runtime-variant decision — neither
  runtime ever read it).

## Figures / runtime

- **K-1** — several figures per deck: inline each fragment through its own
  `FIGS["<id>"]` IIFE wrapper (capture `window.FigTl` immediately per file).
  The fragment file form is `window.FigTl = (gsap) => { … };` — the FIGS
  wrapper must strip the prefix AND the trailing `};`; a dangling `;` left
  between map entries is a SyntaxError that kills the WHOLE inline `<script>`
  (slide count never set, no animations; headless drivers show it only as
  missing AUDIT_RESULT/probe output — check any hand-written FIGS map with
  `node`). assemble.py strips both for you.
- **K-2** — `lib/gsap.min.js` contains `Math.random`/`Date.now` (vendored, harmless —
  whitelisted for any static check; the generated code never calls them).
- **K-3** — the loop is `onComplete → setTimeout(hold) → progress(0).play()`, gated on
  the slide still being active, and cleared on navigation / capture / print. `tl.repeat`
  on the slide timeline breaks the settled end (T-5/T-14).
- **K-4** — figure canvases come from the assets (deck-animation picks the aspect near
  the zone). The deck letterboxes (`preserveAspectRatio` meet) and never rescales text
  inside the SVG.
- **K-5** — figure element ids are SLIDE-SCOPED (deck-animation prefixes them with the
  figure's slide key, e.g. `fs5-…`): several figures inline into ONE document, SVG ids
  and GSAP selectors are document-global — two figures sharing an element id break
  cross-slide selectors. assemble.py FAILs the build on duplicate figure element ids.
- **K-6** — the vendored GSAP 3.14.2 build does NOT interpolate `clip-path` mid-tween
  (verified: the value stays at the `from`-state until the tween ends, then jumps to
  the `to`-state at t=1 — the element looks frozen, then snaps). Runtime effects are
  TRANSFORM/OPACITY only: a wipe = `translateX` inside an `overflow:hidden` wrapper
  (`.fxwipe`, gen_deck), per-line print = per-line opacity spans (`.ln` / `.fxwipe`),
  print CSS = per-line opacity. Do not add clip-path tweens to the runtime or to
  figure fragments (deck-animation inherits the same rule: transform/opacity only).
