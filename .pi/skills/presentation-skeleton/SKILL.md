---
name: presentation-skeleton
description: "Build a presentation skeleton from a talk text. Use when the user provides a transcript, talk text, or the text of the work being presented and wants it structured into slides — «сделай скелет из доклада», «структурируй в слайды», «prepare the slide plan/skeleton from this talk» — or asks for a presentation/deck and no skeleton exists yet. Output: `<name>.skeleton.yaml` (schema v1.1): meta (title, tone, anim_role), slides with content blocks, figure specs, speaker notes, and an animation beat table per slide. Slide count and narrative tone (academic / business / playful / creative) come from a short dialogue with the user — never guessed. The source's academic tone is preserved. Not for rendering the deck (deck-pptx, deck-html) or choosing a design — the design comes from the user as `design.md` (the deck skills' input); the skeleton stays design-free (`design_ref` points at the file and nothing else)."
---

# Presentation skeleton

Turn a talk text into a presentation skeleton: `<name>.skeleton.yaml`. The skeleton is the
single source of content for both render targets (the deck-pptx and deck-html skills) — it
carries content, speaker notes, figure specs, and an animation beat table per slide. It
carries no design.

## Contract

- Input: the source text (transcript / talk text / the text of the work) — `talk.md` in the
  talk folder, or a path the user gives.
- Output: `<name>.skeleton.yaml` in the same folder (folder convention:
  `docs/processes/transcript-to-deck.md`).
- Done when: `scripts/validate.py` and `scripts/text_fit.py` both exit 0 and the coverage
  check in Step 7 passes.

## Steps

### 1. Read the source

Read the whole talk. Note its section structure, its formulas and tables, and the spots
where a diagram, chart, or circuit would carry the meaning (mark them while reading — they
become `figure` slides). Every piece of source content must land somewhere.

### 2. Dialogue (before building)

One compact question, and wait for the answer before writing any file:
- the slide count (no hard cap; 10–15 is typical for a 15–20 min talk),
- the narrative tone (academic / business / playful / creative, …).

`meta.audience` — only if the user volunteers it. If the user's request already states both
values, skip the question.
`meta.anim_role` — infer it from subject + tone (science / engineering / medicine →
factual; marketing / festival / popularization → entertaining; mixed content → mixed).
State the inference in the question or the reply: a wrong inference is cheap to correct,
a missing field is not.

### 3. Structure the slides

Group the talk: one idea per slide. Split a dense section across slides; fold a short
section into one. Section dividers only for genuinely long sections. No slide may exist
only to fill the count.

### 4. Fill content blocks

Per slide: `layout` + `blocks` following the field reference — read
`references/skeleton-format.md` when choosing a layout, filling blocks, or fixing a fit
problem: field dictionary, layout semantics, block types, the fit model. If a slide is
OVER, split it or drop facts — never compress the wording into telegraphese; the
skeleton never shrinks fonts.

Text discipline — the slide states the source's facts, it doesn't comment on them:

- Numbers, names, dates, and legal articles stay VERBATIM from the source —
  rewording is how «без добровольного согласия» becomes «похищено без согласия».
- One fact per line; no invented summary or evaluative lines — a summary belongs
  in `notes`.
- A `text` block is one flowing paragraph — reflow wrapped source lines; hard
  breaks render as-is in the decks.

### 5. Figures

Where the topic carries meaning visually, add a `figure` (`kind`: diagram / chart /
circuit / image) whose `prompt` fully specifies the diagram: elements, connections,
labels, values, and the states it must show. The prompt is the spec the renderer builds
from, so factual content (values, topology, curve shape) must be correct in the prompt
itself. Size the prompt to the embed zone: count the labels — if they do not fit the
side zone readably (labels ≥ 20 px on ≈660×790), cut elements or use layout `diagram`
(the figure IS the slide). Keep `caption` to one short line.

### 6. Animation scripting (the `anim` field)

Every slide gets an `anim` beat table (HTML-only field; the PPTX pass ignores it). Read
`references/animation-scripting.md` before writing beats: the request → description
method (state decomposition, beat columns, settled state), the `anim_role` axis, and the
boundary between what the description says and what the renderer decides. The beat table
says WHAT changes, in WHAT order, with WHAT accent, and what the final static picture
is — never HOW (no mechanisms, libraries, or easings in the skeleton).

### 7. Validate

Run both scripts (from the skill folder or by absolute path):
- `python3 scripts/validate.py <skeleton.yaml>` — schema v1.1 + cross-checks
- `python3 scripts/text_fit.py <skeleton.yaml>` — text-fit estimate per field

Fix every OVER (step 4) and tighten every WARN. Coverage check: re-read the talk and
the skeleton side by side — every section, formula, table, and marked visualization spot
is accounted for (carried, or deliberately dropped and stated in the reply).

## Anti-patterns

- Guessing the count or the tone instead of asking — the dialogue is Step 2, not an option.
- Filler slides (empty dividers, "summary" slides without new content) to hit the count.
- Slogan/interpretive lines absent from the source («Разброс оценок — разные срезы,
  а не конфликт данных:») — a summary, not a fact; it belongs in `notes`.
- A «Метка — значение: детализация; метка2 — значение2» bullet — telegraphese;
  split the slide, not the line.
- Design decisions in the skeleton (colors, fonts, effects) — the skeleton is design-free;
  `design_ref` points at the design file and nothing else.
- `anim` rows that say HOW (mechanisms, library names, CSS) — HOW belongs to the renderer
  skill; the skeleton owns WHAT.
- A beat whose pose is a process ("the current flows") — a pose is a picture: "path A
  drawn, diodes VD1/VD3 accented".
- With `anim_role: factual`, a pose that would be physically false mid-beat (reverse
  conduction, unconnected wire, point off the curve) — every intermediate picture must be
  true.
- Dropping a visualization spot from the source without saying so.

## References

- `references/skeleton-format.md` — read when filling blocks, choosing layouts, or fixing
  fit: the field dictionary, layout semantics, block types, the fit model.
- `references/animation-scripting.md` — read when writing `anim`: state decomposition,
  the beat table, the anim_role axis, the factual/entertaining rules.
- `references/schema.json` — the v1.1 machine-readable schema (used by validate.py).
- `scripts/validate.py`, `scripts/text_fit.py` — execute, do not read.
