# Layout catalog (ticket 09)

A template may be used in an authored deck **only if it is listed here** —
every entry passed the validation protocol below on a dense fixture. The
catalog is the tested layout base: pick from it, or handcraft a slide
(layer-2 authoring route, SKILL.md) — but a handcrafted layout that proves
reusable belongs here after the same protocol.

## Files

- `templates/<name>.slide.html` — the slide source with `{{slots}}` + section
  class `tpl tpl-<name>`. The template file is the single source of the
  slide's structure; validation instantiates it (it never retypes it).
- `templates/catalog.css` — the template CSS, one `/* === tpl-<name> — … */`
  section per template + a `common` section (zone, s-title, bullets, tables,
  code, chips, fig-zone). The assembler's `--styles` input is the `common`
  section + the sections of the templates the deck actually uses.
- `scripts/catalog_check.py` — the validation driver: for every template it
  fills the slots with a dense fixture, assembles a mini-deck (cover +
  fixture) with the ticket-01 assembler and runs the full gate suite
  (assemble guards, content_check, text_audit, visible-content, PDF
  size/pages, R3). Usage: `python3 scripts/catalog_check.py [name …]` —
  exit 0 = all PASS. Fixture decks + frames land in
  `evals/results/layout-catalog/<name>/` (`deck.html`, `qa/s2-t1.png` the
  settled frame, `deck.pdf` the print contract). A re-render over a FAILED
  run first archives the failed output to `<name>/archive/<ts>/`
  (`last-run.json` drives it — the AGENTS.md test-artifact rule).

## Validation protocol (per template)

1. Cut a fixture slide with representative dense content (title + the densest
   block type the layout claims) — the fixture fills the template's slots.
2. Assemble a mini-deck (1–3 slides) with the ticket-01 assembler.
3. Gates: content_check, text_audit, visible-content, PDF size/pages, R3.
4. Full-res review (t0/mid/t1 + print frame) ≤ 3 rounds; fixes go into the
   template, never into the built output.
5. Record the entry here: structure, capacity, usage, provenance, fixture link.

A candidate must be static (no framework/build/interactivity, print-safe
final state), adaptable to the stage contract (1920×1080, one `<section>` per
slide), license-compatible (MIT/Apache free to reuse; AGPL — record
provenance; internal — no license issue).

## Entries

Zone contract for all entries: content zone top 165 / bottom 72 (height
843), left/right `--pad` 72; the in-flow s-title sits at (72,72) in the
0..165 title band (the reference model's `.inner` padding) — per
`layout-constants.md`. Content is vertically CENTERED in the zone by default
(kit default, user rule 2026-10-21); top-aligning is an exception a template
declares — none currently (dense fixtures fill the zone, so centering is
neutral there; sparse content is centered — verified in
`evals/results/deck-skills-retro-2/centering-sparse.png`).

### tpl-title — cover / section divider
- **Structure:** kicker (26px accent, uppercased) + h1 (92px, ≤ 2 lines,
  max-width 1560) + sub (34px, ≤ 2 lines, max-width 1280) + 180×6 accent
  rule; the zone is vertically centered.
- **Capacity:** kicker 1 line; h1 2 lines (~20–24 Cyrillic chars/line at
  92px); sub 2 lines.
- **Usage:** cover and section dividers. Two-line h1 verified in the fixture.
- **Provenance:** generator `layout-section` (gen_deck CONTENT_CSS) — internal.
- **Fixture:** `evals/results/layout-catalog/title/` (gates green).

### tpl-duo-l / tpl-duo-r — text column + side figure
- **Structure:** grid 1032px text column + 24px gutter + 720px figure zone
  (exactly 1920 with the pads); figure zone 720×843, 28px inner padding,
  figfill background + 2px figline border. `duo-l` = text left; `duo-r` =
  mirror.
- **Capacity:** column: bullets 25px/1.55 — up to ~14 lines (dense fixture:
  4 bullets ≈ 8 lines); figure: inner 664×787, aspect ≈ 0.854 (matches
  720×843 figure assets — the fixture hosts a real 664×787 geometry SVG,
  so the settled frame proves the fit, not a text placeholder).
- **Usage:** the workhorse text+figure slide. Put the figure on the side the
  reading flow leaves. The gutter is 24px by contract (72+1032+24+720+72) —
  do not widen it, the grid overflows the zone.
- **Provenance:** generator `layout-content-left` / `layout-content-right` —
  internal.
- **Fixtures:** `evals/results/layout-catalog/duo-l/`, `…/duo-r/`.

### tpl-full — full-width text
- **Structure:** stacked column (gap 24): flowing paragraph (25px/1.55,
  pre-line) and/or formula box (30px, pre-wrap, accent left border).
- **Capacity:** paragraph up to ~10 full-width lines; formula 2–3 lines.
- **Usage:** pure-text slides (no figure, no bullets). Dense fixture =
  paragraph + formula.
- **Provenance:** generator `layout-full` — internal.
- **Fixture:** `evals/results/layout-catalog/full/`.

### tpl-table — table slide
- **Structure:** full-width table (22px; header row figline background;
  even rows rowalt) inside the wipe wrapper (.fxwipe — the clip-path-safe
  wipe per K-6), optional takeaway strip below (accent border).
- **Capacity:** 3 columns × up to 8 one-line rows (dense fixture: 6 rows +
  header + strip, no overflow); cells 1 line (22px), 26px cell padding.
- **Usage:** comparison/method tables. Keep cells to ~30 chars.
- **Provenance:** generator `layout-table` — internal.
- **Fixture:** `evals/results/layout-catalog/table/`.

### tpl-cards — 2×2 card grid
- **Structure:** grid 2×2 (gap 24), cards: figfill background, 1px figline
  border, title 28px + body 25px (pre-line).
- **Capacity:** per card: title 1 line + body up to ~8 lines (dense fixture:
  2 lines; cards stretch to the zone rows).
- **Usage:** 4 parallel concepts. Bodies stay short — 2×2 at 843px zone
  height leaves room for ~8 lines, not 12.
- **Provenance:** generator `layout-cards` — internal.
- **Fixture:** `evals/results/layout-catalog/cards/`.

### tpl-grid5 — five-column enumeration
- **Structure:** grid 5 columns (gap 20), compact cards (title 24px + body
  25px).
- **Capacity:** per card: title 1 line + body up to ~4 lines (340px column).
- **Usage:** enumerations of 5 short items (types, stages). One-line bodies
  are the safe shape.
- **Provenance:** generator `layout-grid-5` — internal.
- **Fixture:** `evals/results/layout-catalog/grid5/`.

### tpl-figure — the figure IS the slide
- **Structure:** figure zone fills the content zone (figfill + 2px border,
  24px inner padding) + caption line (20px, figtext) below it, 72px bottom
  margin kept.
- **Capacity:** figure inner ≈ 1728×~750 (zone 843 − 48 padding − 16 gap −
  1-line caption 28; aspect ≈ 2.3 — the fixture hosts a 1728×751 geometry
  SVG that proves the fit); caption 1–2 lines.
- **Usage:** big diagrams/circuits/charts (deck-animation assets). The
  caption must not touch the slide edge (zone keeps the 72px bottom).
- **Provenance:** generator `layout-diagram` — internal.
- **Fixture:** `evals/results/layout-catalog/figure/`.

### tpl-code — code window + bullets + strip
- **Structure:** stacked column: code window (23px/1.6, pre, `.ln` line
  spans), bullet column (25px), takeaway strip.
- **Capacity:** code 4–8 lines (dense fixture: 4); bullets 1–4 blocks (each
  1–2 lines, pre-line keeps a multi-line block as one bullet); strip 1–2
  lines.
- **Usage:** build/compile snippets, CLI recipes. Code lines must be `.ln`
  spans (print = per-line opacity; whitespace contract — no source newlines
  between tags).
- **Provenance:** real-report slide 10 (13-s10.html), PCB theme — internal
  reference implementation.
- **Fixture:** `evals/results/layout-catalog/code/`.

### tpl-signature — intro + signature + two cards
- **Structure:** centered: intro paragraph (25px, 1480px), signature box
  (30px accent, glow, 1 line), two scards (25px) with the gold corner dot.
- **Capacity:** intro 3 lines; signature ≤ 1 line (~55 chars); per scard
  2–3 lines.
- **Usage:** API/signature reveals (function signature, core command).
- **Provenance:** real-report slide 8 (10-s8.html), PCB theme — internal.
- **Fixture:** `evals/results/layout-catalog/signature/`.

### tpl-pipeline — numbered node chain
- **Structure:** horizontal flex chain: N nodes (400px, chip: head 24px +
  body 25px) with 40px arrow gaps, vertically centered.
- **Capacity:** 4 nodes × (head 1 line + body up to 4 lines) is the dense
  shape (4×400 + 3×40 = 1720px fits; a 5th node overflows — drop to 360px
  nodes or split the slide).
- **Usage:** process/flow slides (input → … → output).
- **Provenance:** real-report slide 12 (15-s12.html), PCB theme — internal.
- **Fixture:** `evals/results/layout-catalog/pipeline/`.

### tpl-verdict — stacked escalation + tail
- **Structure:** centered stack: layers (label 30px right-aligned 360px +
  text 25px 1320px), one `hot` layer (54px gold box with glow), tail line
  (25px, 1560px).
- **Capacity:** 3 layers × (label 1 line + text 1–2 lines) + tail 1–2 lines.
- **Usage:** summary/verdict slides with an escalated focal point.
- **Provenance:** real-report slide 16 (19-s16.html), PCB theme — internal.
- **Fixture:** `evals/results/layout-catalog/verdict/`.

### tpl-chipduo — two structured chips
- **Structure:** centered: criterion line (20px accent, letterspaced) +
  2 chips (head 26px with badge, k/v rows: k 16px accent, v 25px up to
  2 lines).
- **Capacity:** per chip: head 1 line + up to 4 rows.
- **Usage:** comparing two tools/methods on the same criterion grid.
- **Provenance:** real-report slide 4 (05-s4.html), PCB theme — internal.
- **Fixture:** `evals/results/layout-catalog/chipduo/`.

### tpl-quote — centered pull quote
- **Structure:** vertically centered: quote mark (132px accent) + quote
  (64px/1.25, 1560px, pre-line) + source line (24px accent, letterspaced).
- **Capacity:** quote 2–4 lines; source 1 line.
- **Usage:** a framing quote at a section opening or the closing. Density
  rule from the source design: the quote is the slide — nothing else.
- **Provenance:** frontend-slides bold-template-pack quote slide (quote-mark
  + quote-text pair), local copy at
  `evals/prototypes/html-bases/vendor/frontend-slides` (Zara Zhang 2025,
  **MIT**).
- **Fixture:** `evals/results/layout-catalog/quote/`.

### tpl-stat — big number + caption
- **Structure:** centered: number (220px accent) + caption (34px/1.45,
  1440px, pre-line) + optional takeaway strip.
- **Capacity:** number 5–6 chars (1300+ fits; longer digits overflow —
  shrink the font, do not wrap); caption 1–2 lines; strip 1–2 lines.
- **Usage:** one metric per slide (coverage, detector count, speedup).
- **Provenance:** frontend-slides bold-template-pack "massive display
  moment" stat slide, same MIT source as tpl-quote.
- **Fixture:** `evals/results/layout-catalog/stat/`.

## Legacy generator layouts — disposition (ticket 09 acceptance)

All 8 enter the catalog **validated** (none retired):

| generator layout | catalog template |
|---|---|
| `layout-section` | tpl-title |
| `layout-content-left` | tpl-duo-l |
| `layout-content-right` | tpl-duo-r |
| `layout-full` | tpl-full |
| `layout-table` | tpl-table |
| `layout-cards` | tpl-cards |
| `layout-grid-5` | tpl-grid5 |
| `layout-diagram` | tpl-figure |

## No layout repetition

The rule lives in SKILL.md (Per-slide authoring route, spec decision
2026-10-17): the same layout/template on at most one slide of a deck. The
catalog's 15 tested structures exist to make that rule satisfiable. On the
authoring route `congestion.py`'s layout counter reads the SKELETON `layout`
— a content-shape hint, not the rendered template: repetition of RENDERED
structure is judged in the visual review by section classes (tpl-*/h-*);
a handcrafted class is not an escape from the comparison.

## Adding a template

1. Author `templates/<name>.slide.html` (section `slide tpl tpl-<name>`,
   slots `{{…}}`, `reveal` + `data-beat` on the structural elements) and the
   `tpl-<name>` section in `catalog.css` (tokens only — no hardcoded
   theme colors; the whitespace contract applies).
2. Add a dense fixture (title + fields + slot values) in
   `scripts/catalog_check.py` and register it in `TEMPLATES`.
3. `python3 scripts/catalog_check.py <name>` — gates green, then the full-res
   review loop (t0/mid/t1 + print) with fixes in the template.
4. Record the entry in this file; only then may decks use it.
