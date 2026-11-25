---
name: deck-html
description: Build a deterministic HTML presentation deck (+PDF) from a validated presentation skeleton (YAML, presentation-skeleton format) and a design (design.md → tokens + effects). The frontend_slides base (1920×1080 scaled stage), vendored GSAP D2 runtime, per-slide timelines, figures from the deck-animation skill, settled print contract, R3 byte-stable captures, no layout drift, no scroll, no interaction. Use when the user wants the HTML render target of an existing skeleton («сделай HTML-версию из скелета», «build the HTML deck from this skeleton», «HTML deck + PDF»). Not for building the skeleton (presentation-skeleton), not for the PPTX target (deck-pptx), not for figure authorship (deck-animation — invoked by this skill when assets are missing).
---

# deck-html

Builds one render target: an HTML deck — a **true single file** (`deck.html`: CSS,
GSAP, slide markup, settled figure SVGs and fragments inlined, font subsets
base64-embedded) plus a **PDF** (one page = one slide, 1920×1080). Stability bar:
no layout drift across re-renders, reliable PDF, clean minimal HTML, informative
unobtrusive animations, keyboard navigation only.

## Inputs

| input | from | contract |
|---|---|---|
| skeleton | presentation-skeleton | `<name>.skeleton.yaml`, schema v1.1; hard gate `scripts/validate.py` |
| design | user / DS | `design.md` → `tokens.json` (+ optional `effects.css`) — the theme package; see `references/design-tokens.md`; worked example `scripts/themes/noir.tokens.json` |
| figures | deck-animation | per drawable slide: `assets/fig-<id>.{svg,manifest.json,tl.js,png}` |

`meta.anim_role` (factual / entertaining / mixed) is SET by the skeleton; **this
skill interprets what each value means** for motion and loop gating — see
`references/animation-methodology.md`. The skeleton stays design-free and mechanism-free.

## Workflow

**Route (decide first):** the **per-slide authoring route** (the section
below) is the DEFAULT route — one authored slide file per slide, a catalog
layout or a handcrafted composition per slide. The generated route (step 3
with `gen_deck.py`) runs ONLY when the user explicitly asks for it (a quick
draft, or the legacy 8-layout vocabulary). One deck is built with exactly
ONE route — the two are never mixed in one deck. Do not ask the user which
route they want: authoring is the answer unless they say otherwise.

1. **Validate** — `python3 scripts/validate.py <skeleton.yaml>`. A failing skeleton
   is not a skeleton: stop and report.
2. **Figures** — for every slide with a `figure` (kind diagram / chart / circuit),
   the asset set must exist in the run dir's `assets/`. If not: follow the
   **deck-animation** skill (read its SKILL.md) to produce the assets. This target
   consumes the SVG + the fragment; the PNG is part of the asset contract (the
   PPTX target needs it).
3. **Generate** — *generated route only* (on the default authoring route the
   assembly step in the section below replaces this step):
   `python3 scripts/gen_deck.py <skeleton.yaml> --theme <tokens.json> [--effects <effects.css>] [--figs <assets-dir>] <out.html>`
   The generator emits the single file and warns on every placeholder figure panel.
   An 8-layout set is implemented (section, content-left, content-right, full,
   table, grid-5, cards, diagram); an unknown layout is a generator error.
   The generator stays as the geometry reference and the test-stand baseline —
   its CONTENT_CSS is read, never edited.
4. **Content QA** — `python3 scripts/content_check.py <skeleton.yaml> <deck.html>`:
   every skeleton text field must appear in its slide; no placeholder panels, no
   figure-prompt leaks, no external references, and every `<section>` tag is
   well-formed (class attribute intact — G-1). Must pass before rendering.
5. **Layout QA (hard gate)** — `python3 scripts/text_audit.py <deck.html>`:
   no text overflow past the 1920×1080 stage, no text-on-text overlap in the
   settled state (border-grazing is not a collision — the exact thresholds in
   `references/animation-methodology.md`). `GATE text-audit PASS` = 0
   problems; each problem is named by slide id + a pair of selectors.
   Intentional overlay text (badges, page numbers) opts out with `data-ov`;
   `--probe <sel>` prints geometry for a named selector (diagnostics).
6. **File QA (hard gate)** — `bash scripts/render_html.sh <deck.html> <outdir> [N] [MID_SLIDE]`:
   every settled frame must carry visible content (the black-screen class,
   F-H5), PDF page size must be `1440 x 810 pts` (1920×1080 px
   — the F-P1 `@page` rule), pages == N, and the R3 double-capture must be
   md5-identical. A failing gate is a broken deck: copy the broken state to the
   run dir's `archive/` **before** any in-place fix (repo AGENTS.md rule).
7. **Visual review loop** — review at FULL resolution (96-dpi chat previews ghost —
   F-H1): `s<i>-t1.png` (settled, the main frame), `s<i>-t0.png` (cold),
   `s<MID>-mid.png`, and the PDF pages (print freeze: settled figures, no
   `.flow-el`). Frame names follow the frame protocol (slide position, not the
   skeleton id — `references/animation-methodology.md`).
   **Congestion (run on the skeleton, after every skeleton change):**
   `python3 scripts/congestion.py <skeleton.yaml>` — per-slide text fill %
   (chars vs a per-layout capacity model) + the layout-grammar counter
   (how many slides share one layout). It flags **EMPTY (<40% fill)** and
   **CROWDED (>95%)** and prints the fill spread + the most repeated layout —
   the "congestion/emptiness" metrics. It is a HEURISTIC review input, not a
   hard gate: a flag means look at that slide's frame, not that the build is
   broken. On the authoring route the counter reads the SKELETON `layout` — a
   content-shape hint, not the rendered template: repetition of RENDERED
   structure is judged in the visual review by section classes (tpl-*/h-*); a
   handcrafted class is not an escape from the comparison.
   **Type floor (run on the built CSS, after every build):** `python3 scripts/type_floor.py <deck.html | theme.css slides/*.html>` — body
   font-size floor (25 px) audit: names sub-floor body selectors as REVIEW
   WARNINGS (chrome whitelisted); read them here, never a hard gate.
   Figure slides: check the mid frame against the beat table (the beat's complete
   pose at the beat center). Fix in the sources (the generator, or the slide
   files on the authoring route) / tokens / effects / figure assets — never
   patch the built `deck.html`, never modify the skeleton. Re-render only
   changed slides.
8. **Report** — per slide: layout, reveal, figure integration (loop on/off),
   residuals; gate results.

## Per-slide authoring route

This is the DEFAULT route (the Route line above the Workflow). The generated
route is the opt-in exception, for when the user explicitly asks for the
8-layout vocabulary. One deck is built with exactly one route.

Two-layer model:
- **Layer 1 — machine (the script):** stage, runtime, print contract,
  single-file assembly. `scripts/assemble.py` emits it; never hand-write it.
- **Layer 2 — the slides (the author):** one file per slide, `NN-<id>.html`
  (sorted order = deck order), each holding one
  `<section class="slide <layout-word> [extra...]" id="<skeleton-id>">`.
  The theme CSS (the design system / component kit built from design.md + the
  per-slide layout rules) is passed via `--styles`; the author writes
  components, not boilerplate.

```
python3 scripts/assemble.py <slides-dir> <out.html> --tokens <tokens.json> --styles <theme.css> [--effects <effects.css>] [--figs <assets-dir>] [--skeleton <skeleton.yaml>]
```

- `--skeleton` enforces the slide ids and file order (and sets `<title>` /
  `<html lang>` from `meta`).
- Figures: at most one `<!--FIG:<fid>-->` marker per slide, `<fid>` = the
  section id (the runtime looks up `window.FIGS` by section id); assets
  `fig-<fid>.{svg,tl.js}` as in step 2. The fragment file is
  `window.FigTl = (gsap) => { ... };`.
- `--runtime` defaults to `runtime-noloop.js` (slide activation is the only
  animation trigger — play once, never replay); pass `scripts/runtime.js`
  only for a deck whose user-stated policy wants T-14 figure replays. The
  Rules' loop lines describe the loop-capable runtime; on this route the deck
  stays loop-free until opted in. A loop-free deck (activation-only
  playback) is a fully conforming configuration — the real-report deck is
  built exactly that way.
- Slide shell: `.inner{position:absolute;inset:0;padding:var(--pad)}` inside
  the section; the title sits in the 0→165 band — one line, or add `title-2`
  to the section class and shift the zones down yourself (L-1; the generator
  does it automatically). A zone figure's caption is placed by the author's
  layout (figcaption has no default position). The theme CSS keys per-slide
  rules by the section id (`#s12 .zone{…}`) or by a layout class
  (`.slide.duo-r .zone{…}`).
- Reference model: read `scripts/gen_deck.py` CONTENT_CSS when wiring the
  theme CSS — the generated route is the reference implementation (read, don't
  edit).
- Whitespace: skeleton newlines are the rendered line structure — the
  per-class `white-space` contract (pre-line / pre-wrap / structural lines,
  the doubled-blanks trap) is in `references/layout-constants.md`.
- Gates are unchanged: content_check (step 4), text_audit (step 5),
  `render_html.sh` (step 6) and the visual review loop (step 7) apply to the
  assembled deck exactly as to the generated one.
- **No layout repetition (authoring route):** the same layout/template must
  not appear on two slides of one authored deck — the congestion counter
  reads the SKELETON `layout` (a content-shape hint, step 7), so repetition
  of RENDERED structure is flagged in the review by section classes
  (tpl-*/h-*) — a handcrafted class is not an escape. The generated route
  keeps its 8-layout vocabulary.
- **Templates:** a slide may use a template only from the validated catalog —
  `references/layout-catalog.md` (the entries, their content capacity, usage,
  instantiation and the add-a-template protocol; every entry passed the
  fixture validation protocol, and the 15 tested structures exist to keep the
  no-repetition rule satisfiable). A handcrafted layout that proves reusable
  enters the catalog through the same protocol before it may be reused
  elsewhere.

## Artifacts

Run dir `evals/results/<run>/` (or the user's dir): `deck.html` (the single file),
`deck.pdf`, `assets/` (figure source sets), `qa/` (frames + contact sheet),
`work/` (transients). Broken states → `archive/` before in-place fixes.

## Rules (short list — details in references/)

- GSAP D2 only; one paused timeline per slide; no infinite tweens inside timelines
  (loops are the deck-level restart, T-14); no scroll-driven effects; no interactive
  elements; deterministic (R3: same `?slide=&t=` → md5-identical).
- Text: a compact block wave in ALL roles (titles first); text slides never loop.
- Figures: settled SVG inlined (with JS off the picture must already be final —
  print-safe by construction); fragment inlined per figure through the `FIGS`
  wrapper; the deck letterboxes, never crops.
- Loop policy: looping is an explicit deck-level decision, never a role
  default. The default runtime (both routes) is loop-free — with no loops,
  slide activation is the ONLY animation trigger (play once on enter, restart
  on re-enter). The T-14 loop-capable runtime is selected only when the
  user's stated policy asks for figure replays (assemble `--runtime
  scripts/runtime.js`; gen `--loop`); on such a deck figure slides replay
  after a 1.5 s hold and the user's policy wins over any role default.
- Print: the settled state is guaranteed by CSS + the authored SVG base, not by
  runtime state (F-P2); `.flow-el` hidden; `@page 1920px 1080px`.
- `anim_role` in deck-html: factual — the beat table is the source of truth, the
  PDF must read as a static printout; entertaining — motion may carry
  atmosphere (loops only under the loop policy above); mixed — per slide.
  The role never implies loops (loop policy above).

## Anti-patterns

- Patching the built `deck.html` in place (edit the sources — generator, slide
  files, tokens, assets — and rebuild; authoring slide files from scratch is
  the per-slide authoring route, not a patch).
- Verdicts from low-resolution previews (ghosting).
- CSS animations for content motion (D2 only; CSS is the static print contract).
- CSS transitions on slide visibility (stall at 0 in headless captures — C-4).
- A figure fragment that leaves the picture incomplete at TOTAL (settled = complete).
- A loop on a text slide (any role).
- A PDF that differs from the settled screen state (print contract).
- Shrinking fonts to fit (overflow is fixed upstream, in the skeleton).

## References

- `references/layout-catalog.md` — the validated layout templates (15): entries
  with capacity and usage, provenance, the fixture validation protocol and the
  add-a-template path. Read when choosing or extending a layout on the authoring
  route.
- `references/layout-constants.md` — the 1920×1080 model, the eight layout zones,
  the type scale, the @page/print PDF contract. Read for layout or overflow problems.
- `references/design-tokens.md` — the theme package contract (tokens + effects),
  font embedding, the factura layer. Read when wiring a design.md.
- `references/animation-methodology.md` — D2 rules, the T-numbers, the anim_role
  interpretation, figure integration mechanics, the frame protocol, the print freeze.
  Read when wiring motion or debugging frames.
- `references/gotchas.md` — accumulated findings (F-*, S-*, C-*, K-*). Read when
  something is broken but nothing "should" be.
