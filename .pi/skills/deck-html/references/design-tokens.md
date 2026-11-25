# Design tokens + effects (the theme package)

A design is a **theme package**: `tokens.json` (values) + optional `effects.css`
(factura). Ticket-06 rule: apply the DS factura, not just the tokens — a token set
without its effects layer is a different design.

## tokens.json contract

| key | type | meaning |
|---|---|---|
| `stage_bg` | color | the area around the stage (usually darker than the slide) |
| `slide_bg` | color | slide background — explicit, never transparent |
| `title` | color | slide titles |
| `body` | color | text |
| `accent` | color | informative highlights (one accent) |
| `accent_glow` | color | accent glow rgba (decor, subtle) |
| `figfill` | color | figure panel background (opaque) |
| `figline` | color | figure borders / base strokes |
| `figtext` | color | figure labels / captions |
| `rowalt` | color | alternating table rows |
| `headertext` | color | table header row text |
| `font_family` | string | family name used by the embedded @font-face |
| `font_stack` | string | CSS font stack (family first, then fallbacks) |
| `pad` | number | page padding px (default 72) |
| `fonts` | [{file, weight, style?}] | woff2 subset files embedded base64 into the HTML |

Dark-theme discipline (P0, from the PPTX runs): `slide_bg` explicit, table rows/cells
explicit fills (`rowalt`), no reliance on browser defaults.

## Font embedding (single-file rule)

The generator embeds each `fonts[]` entry as a base64 `@font-face` data URI. Rules:

- Ship **latin + cyrillic subsets** for each weight the deck uses (the fixtures are
  RU). The generator derives `unicode-range` from the subset name in the file name
  (`latin` / `cyrillic`); a file with no subset token gets no range (whole font).
- Standard ranges: latin `U+0000-00FF, U+2070-209F, U+20AC, U+2122, U+2212,
  U+FB00-FB06`; cyrillic `U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116`.
- If the theme names no font files → system stack, no embedding (the deck is still
  self-contained; fonts are a design decision).
- Type-scale floor: flowing body text is ≥ 25 px at 1920×1080
  (`references/layout-constants.md`, type scale) — audited by `scripts/type_floor.py`
  (review warnings, not a gate); raise body classes in the theme, don't tolerate them.
- Cyrillic coverage: without a cyrillic subset the text silently falls back to a
  different font — metric drift mid-sentence. Check the glyph coverage of the
  design's script before freezing the package (D-2..D-7, ticket 06).

## effects.css layer (factura)

A plain CSS file, inlined after the token CSS. Factura rules:

- static elements over moving ones (z-order), decor behind content with managed
  z-index;
- **every loop is frozen in `@media print`** (animation: none / settled state);
- contrast preserved — effects never dim body text below readable;
- keep it small: effects are the DS's texture (corners, grain, glows), not layout.

Worked example: `scripts/themes/noir.tokens.json` + `noir.effects.css` (noir = clean,
near-empty effects file — a package may carry zero effects). The cassette stress-test
case (scanlines + corner cuts) is the non-trivial reference in
`evals/prototypes/stress/themes/cassette.effects.css`.
