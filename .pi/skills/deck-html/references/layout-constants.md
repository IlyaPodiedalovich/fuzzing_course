# Layout constants (1920×1080 model)

## The model

- Authored space: **1920×1080 px** (16:9). The stage is scaled as a whole by JS
  (`transform: translate scale`); content is laid out at 1920×1080 and never reflows
  per device. Captures run at DPR 1, window 1920×1080, stage pinned 1:1.
- Vendor base CSS (`scripts/lib/viewport-base.css`) owns: viewport lock, the scaled
  stage, the stacked slides, the **print stacking** (one slide per page, `break-after:
  page`). Do not rewrite it; extend it in the generated content CSS.

## Zones (px, in authored space)

| zone | value |
|---|---|
| padding (`--pad`) | 72 |
| title band | top 0 → 165 (title baseline zone) |
| content column | top 165, bottom 72, width **1032** (content-left: left; content-right: left 816) |
| side figure zone | top 165, opposite side, **720 × 843** (aspect ≈ 0.854), figfill bg + 2px figline border + 28px padding |
| table layout content | top 165, width **1776** |
| full layout with figure (figure below) | text zone top 165 height ≈ 380; figure zone top ≈ 560, width 1776, height ≈ 450 (wide, aspect ≈ 3.9) |
| diagram layout | figure zone top 165, left/right 72, bottom 140 (full width) + caption line |
| section layout | kicker 26px / title 92px / sub 34px / accent rule 180×6 |

### Title band and two-line titles (L-1)

The 0→165 title band is sized for a **one-line** 56px title. Long titles are the
overlap risk, not the fonts:

- Title width per layout: `content-left` → max-width 1032 (stays above the text
  column); `content-right` → width 1032, margin-left 744 (816 zone − 72 inner
  padding, i.e. above the right text column); `full`/`table` → max-width 1776.
  The title never spans across the figure zone.
- The generator estimates line count (chars per line at 56px Montserrat: 33 for the
  1032 columns, 61 for 1776-wide layouts) and adds the `title-2` class when ≥ 2
  lines → zones shift down: content/figure/cards top 165 → **250**; full: text
  height 380 → 270 and figure zone 560 → 470; diagram: text height 190 → 100 and
  figure zone 390 → 450; title margin-bottom 40 → 20.
  The estimate is for Latin; Cyrillic is wider (~10–15% fewer chars per line) —
  verify a two-line title at full resolution before trusting it.
- Invariant: a title either fits the band (one line) or shifts the zones (two
  lines). Never overlaps a zone. On the authoring route the author adds `title-2`
  + the zone shift themselves (the generator does it automatically).

Figure SVGs letterbox inside their zone: `preserveAspectRatio="xMidYMid meet"` on a
`width:100%;height:100%` SVG — the figfill background shows in the strips. Canvas
aspect comes from the figure asset (deck-animation picks it near the zone aspect);
the deck never crops.

## The eight layouts (skeleton schema)

`section`, `content-left`, `content-right`, `full`, `table`, `grid-5`, `cards`,
`diagram` — shapes as in presentation-skeleton's `skeleton-format.md`. The generator
implements all eight; unknown layout = generator error (fail loud, never guess).

## Type scale (verified in the stress test with denser content than the fixtures)

title 56 (section 92), bullet 25, text 25, formula 30, card title 28 / body 25,
table 18 (header 18 bold), figure caption 20, page number 18. **The skeleton never
shrinks fonts and neither does the generator** — overflow is fixed by splitting the
slide or trimming the wording (upstream, in the skeleton), not by smaller type.
**Floor (user decision 2026-10-21):** flowing body text — bullets, paragraphs,
card bodies, grid bodies, strips, chip values — is ≥ 25 px at 1920×1080, audited
mechanically by `scripts/type_floor.py` (REVIEW WARNINGS, not a hard gate; its
CHROME set is the authority for the list below).
Explicit CHROME outside the floor: table cells (18–22 px), figure/card
captions (18–20 px), page numbers (18 px), kickers/badges/labels (16–20 px),
code windows (23 px — dense mono; revisit if a run complains). A theme CSS
whose body classes sit below the floor is raised in the theme, not tolerated.

## The whitespace contract (skeleton newlines are authoritative)

Skeleton block newlines are the rendered line structure: the settled slide
shows exactly the skeleton's lines — no doubled blank lines, no collapsed
lists, no wrapping that breaks a token. Three encoding strategies:

- **Flowing multi-line text** (author text classes: bullets, notes, strips,
  captions): `white-space: pre-line` on the class. The skeleton `\n` renders
  as a line break; stray source whitespace collapses; long lines may still
  wrap. Default for every multi-line text class in the theme CSS — the
  generated route's flowing paragraphs are the exception (single-line
  semantics), author classes are not.
- **Code / formula (`pre` blocks):** `white-space: pre-wrap` (`.formula`,
  real-report build-issues #5) or `pre` (code). Each line is its own element
  AND a block: `.ln{display:block;min-height:1.2em}` in the theme CSS (the
  generator emits this in CONTENT_CSS) — without the block rule the per-line
  `.ln` spans glue into one inline line. In a hand-authored `pre` code block
  the line spans are written with the newline INSIDE the span text at line
  end and NO source newline between tags:
  `<span class="ln">line one\n</span><span class="ln">line two\n</span>` (a
  source newline between tags in a `pre` block renders as an extra blank
  line — the doubled-blanks bug; the real-report code blocks are the
  reference shape). Each line span is its own `.reveal` — the per-line type
  effect (`fx: type`).
- **Structural lines (the generator's default for bullets and type blocks):**
  each skeleton line is its own element (`<li>`, `<p class="ln">`) — the line
  break becomes markup, no white-space rule needed. An INDENTED bullet line
  (exactly two leading spaces) is a sub-item, level 2 — indented, smaller
  marker (class free to author; the contract is the indent); any other
  leading-space count is undefined (renders level 1).

Gate note: the gate's whitespace normalization (the substring rule below)
means it CANNOT catch line-structure drift — a 6-line list collapsed into
one paragraph passes it. Line structure is verified in the settled review
frame (step 7, full resolution).

## The content_check substring rule (skeleton text vs markup)

The gate (content_check) checks, per slide: the slide title, and each block
field — after whitespace normalization (all whitespace collapsed to single
spaces on BOTH sides — the markup may add or drop any whitespace, but not
insert foreign text between the field's lines). Per-type granularities
(= the `expected_texts` check set):

- `text` / `formula` (+caption) / `card` (title + body) blocks and the slide's
  figure caption: the WHOLE field must appear as a CONTIGUOUS substring of
  the slide's tag-stripped text.
- `bullet` blocks: each line separately (each line an independent substring —
  the bullet list may be reflowed more freely, but no line may be missing or
  have foreign text welded onto it).
- `table` blocks: every cell (columns + rows) individually.

The gate checks only the skeleton → slide direction: extra text in the slide
passes, missing or split-up skeleton text fails with the field name.

Safe operations when reorganizing a field's markup:

- **Split** one field's lines into separate elements, keeping the ORDER:
  `<p>L1</p><p>L2</p>` — the tag-stripped text is still contiguous.
- **Reorder** lines only if you reorder the skeleton field to match (the
  skeleton stays the source of truth — upstream fix, never a markup hack).
- **New visible labels** (card heads, kickers, annotations) are added as
  separate skeleton fields — never injected between the lines of an existing
  field (an injected label between lines is foreign text → the field's
  substring breaks → the gate fails on that field). A label placed BEFORE or
  AFTER a field's lines is safe for that field's contiguity, but a label that
  isn't a skeleton field is untracked text — add it as a field so the gate
  checks it too.

Worked example (real-report slide 10, 2026-10-17): a 6-line wall of text was
reorganized into a centered paragraph + a sigbox + two chips — every line
kept verbatim, only the elements changed (same order), no label injected
between lines → content_check green with the same skeleton.

What the gate CANNOT see: text that is in the slide but not in the skeleton
at all — a label placed before/after a field's lines passes. That is the
fidelity gap: the skeleton is the single source of content for both render
targets (the presentation-skeleton skill), so every visible label must enter
the skeleton as its own field — added there first, then placed in the markup.

Contract test: `tests/test_content_check_contract.py` (recipe green;
injected label between lines red and named).

## Print / PDF contract (F-P1)

- `@page { size: 1920px 1080px; margin: 0 }` → PDF page = 1920×1080 px =
  **1440 × 810 pt** (96 dpi). Without this rule Chromium prints Letter pages and
  clips every slide at the right edge.
- Chromium flags: `--no-pdf-header-footer --force-device-scale-factor=1
  --window-size=1920,1080 --virtual-time-budget=9000 --print-to-pdf`.
- Gates (render_html.sh, hard): pdfinfo `Page size: 1440 x 810 pts` and
  `Pages == N_slides`; print media shows every slide in its settled state (CSS +
  authored SVG base — not runtime timeline state; F-P2 in gotchas.md).
