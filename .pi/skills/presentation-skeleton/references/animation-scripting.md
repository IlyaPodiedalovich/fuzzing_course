# Animation scripting (the `anim` field)

The `anim` field is the skeleton's only animation artifact: a **text description**
(a beat table) of what the audience sees, in what order, and what the final static
picture is. The renderer skill (deck-html) turns it into motion and owns every
mechanism (HOW). This file defines WHAT the description must contain.

## The anim_role axis

`meta.anim_role` sets the informational weight of animations and infographics:

- **factual** (science, engineering, medicine, …) — the animation is part of the
  explanation. Every pose must be factually correct, **including intermediate beats**:
  no reverse conduction, no unconnected wire, no point off the curve, no value that
  contradicts the diagram. The beat order is the explanation order. No decorative
  loops. The settled picture must carry the complete fact — a factual deck must be
  readable as a static printout.
- **entertaining** (festivals, marketing, popularization) — motion may carry
  atmosphere and emphasis; decorative loops are allowed; beats may serve rhythm, not
  just information. The infographic content is still correct — the role changes the
  style of motion, never the truth of what is drawn.
- **mixed** — apply per slide: figure slides follow the factual rules, text/title
  slides may use the entertaining style.

## Method: request → description

The input for a slide's beats is the slide's own content: its figure prompt, its
blocks, and the point the slide makes. Derive the beats from them.

**State decomposition.** List the stable visual states the audience must see as
pictures. A state is a *pose*, not a process: element visibility, colors, positions,
path draw progress, labels, values. If a state cannot be described as a still
picture, it is not a state — split it into the pictures that compose it.

**Beat table.** One entry per beat:

```yaml
- id: b1            # b0, b1, … in order
  pose: |           # prose -> block scalar (see skeleton-format.md, YAML discipline)
    the complete picture AFTER this beat
  change: only what changes during the beat; everything else holds
  accent: what the eye should follow (null if none)
```

Rules:
- `b0` is the **cold base** — the elements present from the start, usually dimmed.
- The last state is `settled` — the final picture; it is the one that goes to print.
  For factual slides it must carry the complete fact (see the axis above).
- `duration` — the slide length in seconds (default 6). Each informative beat needs
  real time (≈ 1.5 s minimum for a beat that introduces new content); set duration
  from the beat table, not the other way round.
- One beat per meaningful state change. Do not choreograph what the content does not
  need — a beat exists to show a fact, not to fill the seconds.

### Text slides (no figure)

Keep the wave compact: `b0` title visible, `b1` the blocks appear as one fast wave
(order by visual position, top to bottom). Total wave ≲ 1 s; text carries no meaning
and must not drag attention. Text slides never loop (the renderer enforces it; the
description simply has no loop to describe).

### Figure slides (factual)

Walk the explanation: each informative beat ends in a pose a listener could
photograph and understand on its own (state of the circuit, position of the point,
labels shown). Check every pose against the facts of the figure prompt before
finishing: values, conduction, connectivity, curve position.

## What belongs here / what does not

- **Here:** states, their order, accents, duration, the settled picture.
- **Not here:** mechanisms (draw, stagger, easing), libraries, CSS/JS, loop policy,
  capture flags, timing engines — the renderer decides them from the beat table.
  A beat table that names HOW has drifted out of the skeleton.

## Example (factual, figure slide)

The T2 rectifier request: «show which diodes conduct in each half-cycle and how
current flows through the load» →

```yaml
anim:
  duration: 6
  beats:
  - id: b0
    pose: |
      cold base: source, bridge (dim diodes), rails, load R, waveforms panel,
      direction arrows
    change: base rises in
  - id: b1
    pose: |
      VD1+VD3 lit; path A drawn; label «positive half-cycle»; flow along A
    change: diodes → accent, path A drawn, flow starts
    accent: path A + VD1/VD3
  - id: b2
    pose: |
      VD2+VD4 lit; path B; label «negative half-cycle»
    change: A dims, B drawn, flow on B
    accent: path B + VD2/VD4
  settled: |
    both paths (B bright, A muted), all four diodes (pair B bright, pair A soft),
    label «both half-cycles → load»
```
