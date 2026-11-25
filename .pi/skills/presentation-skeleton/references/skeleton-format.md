# Skeleton format (schema v1.1)

The skeleton is YAML. The machine-readable schema lives next to this file
(`schema.json`) and is enforced by `scripts/validate.py`. This file is the human
dictionary: what each field means and how to use it.

## Top level

```yaml
skeleton_version: 1        # always 1
meta: { … }                # one object, see below
slides: [ … ]              # ordered list, see below
```

## meta

| field | required | meaning |
|---|---|---|
| `title` | yes | The deck title — taken from the talk, not invented |
| `audience` | no | Only when the user named the audience |
| `lang` | yes | Language of the deck, default `ru` |
| `target` | yes | `pptx` or `html` — the render target the skeleton is tuned for first (text density, figures). Either deck skill can consume the skeleton; the PPTX pass ignores `anim`. |
| `canvas` | no | Aspect ratio, default `16:9` |
| `design_ref` | no | Name of the design source file next to the skeleton, default `design.md` |
| `tone` | yes | Narrative tone chosen with the user: academic / business / playful / creative / … |
| `anim_role` | yes | `factual` / `entertaining` / `mixed` — see `animation-scripting.md` |
| `source` | no | Path of the source text |

## slides[]

| field | rule |
|---|---|
| `id` | `s1`…`sN` in order; a section divider is `sec-<slug>`; the title slide is `t` |
| `title` | The slide's TOPIC in one short phrase (5–8 words) — not a section label, not a slogan |
| `layout` | one of the eight below |
| `blocks` | required for every layout except `diagram` and `section` |
| `figure` | `null` or the figure object (see below) |
| `anim` | `null` or the beat table (see `animation-scripting.md`) — usually present |
| `title_fx` | Optional: the slide-title reveal effect — `flicker` (cover/section default) / `mask` (content-title default) / `print` / `fade-up`; the deck-html runtime vocabulary (deck-html `references/animation-methodology.md`) |
| `notes` | Speaker notes: what the speaker says (may be `null`) |
| `caption` | Rare: one short line under the whole slide |

### Layout semantics

| layout | shape | use for |
|---|---|---|
| `content-left` | text column left, figure right | text + diagram/chart pair |
| `content-right` | text column right, figure left | same, mirrored |
| `full` | full-width content | dense text, big formulas, wide tables |
| `table` | table slide | a table is the content |
| `grid-5` | up to 5 cards in a row | enumerations (5 items max, short bodies) |
| `cards` | 2–4 larger cards | concepts with a title + a short body |
| `diagram` | full-slide figure | the figure IS the slide (labels live in the figure) — legitimate when the figure is the slide's point or would not read beside the text; not the default for every figure (the default is text + figure, `content-left`/`content-right`) |
| `section` | title + one line | long section breaks only; the title slide (`id: t`) uses it |

## blocks[]

| field | rule |
|---|---|
| `id` | `a0`, `b0`, … lowercase, unique within the slide |
| `type` | `bullet` / `text` / `formula` / `card` / `table` |
| `text` | for `bullet` (a list of short items, one per line; an INDENTED line — exactly two leading spaces — is a sub-item, level 2; any other indent is undefined and the validator passes it as-is), `text`, `formula` |
| `text` (for `type: text`) | A flowing paragraph — one flow: no hard break inside a sentence, breaks only between semantic units (lists belong in `bullet`; `formula` keeps its line structure) |
| `title` + `body` | for `card` |
| `columns` + `rows` | for `table` (rows = arrays of strings, one per row) |
| `caption` | optional small line under the block |
| `beat` | Optional: `b0`…`bN` — groups the block's reveal into a per-beat wave (a 0.45 s pause between beats; the deck-html runtime); by convention it references an id of the slide's `anim.beats` table (validator enforces the `b0`-first ordering); without it the slide is one wave |
| `fx` | Optional: the block's reveal effect — `print` (instant console line) / `mask` (slide-in wipe, translateX behind an overflow mask — clip-path is dead in the vendored GSAP) / `type` (legacy alias of mask) / `flicker` (CRT flicker-in) / `fade-up` (the default); the deck-html runtime vocabulary |

### YAML discipline

Prose fields (`text`, `prompt`, `pose`, `change`, `accent`, `settled`, `notes`,
captions) go in a **block scalar** (`|`) or in quotes — prose contains `: ` and
breaks plain YAML. Short tokens (ids, enum values, numbers) stay plain.

```yaml
pose: |
  cold base: axes, dim curve
```

The validator hints at this when a file fails to parse; a skeleton that does not
parse is not a skeleton.

### Text-fit budget

`scripts/text_fit.py` estimates capacity per field on the 1280×720 canvas: margins 4.5 %,
title zone 96 px, footer rail 36 px, body font 24 px, small text (tables, cards) 18 px,
85 % of the geometric capacity counts as usable (±30 % accuracy by design). One field
OVER → split the slide or drop a fact — a line is never compressed into telegraphese. The skeleton never compensates with smaller
fonts — font sizes are a design decision, not a skeleton field.

## Minimal example

```yaml
slides:
- id: s3
  title: Проводимость: диод открывается после колена
  layout: content-right
  blocks:
  - id: a0
    type: bullet
    text: |
      До колена (≈ 0.7 В для Si) ток ничтожно мал
      После колена: малое dU даёт большой dI
  - id: a1
    type: formula
    text: I = I₀ · (e^{U/U_T} − 1)
  figure:
    kind: chart
    prompt: |
      ВАХ диода: ось U (В, 0…1.0), ось I (мА, 0…10); кривая — плоская до колена
      ≈ 0.7 В, затем экспоненциальный рост; пометка колена; обратная область
      (U < 0) — ток ≈ 0. Форма кривой качественная, значения колена и оси обязательны.
    caption: ВАХ кремниевых диодов
  anim:
    duration: 6
    beats:
    - id: b0
      pose: |
        cold base: axes, ticks, labels, dimmed curve
      change: base rises in
    - id: b1
      pose: |
        knee note visible, curve flat part drawn, point at the knee
      change: curve draws to the knee (0.7 V), note appears
      accent: knee point
    - id: b2
      pose: |
        full curve drawn, traveling point at (0.9, 10), live readout 0.90 В / 10.0 мА
      change: curve draws to the end, point travels, readout updates
      accent: traveling point
    settled: |
      fully drawn curve, knee note, point at the final operating point, readout
      final values
  notes: |
    Подчеркнуть: колено у Si около 0.7 В, у Ge — 0.3 В
```
