---
name: deck-pptx
description: "Use this skill any time a .pptx or .potx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx or .potx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates (.potx), layouts, speaker notes, or comments. Trigger whenever the user mentions \"deck,\", \"slides,\", \"presentation,\", or references a .pptx or .potx filename, regardless of what they plan to do with the content afterward. If a .pptx or .potx file needs to be opened, created, or touched, use this skill. In this project the main use is the skeleton pipeline: input is a presentation skeleton (skeleton.yaml) plus a design.md; output is deck.pptx AND deck.pdf (see the \"Skeleton to deck\" section)."
---

# PPTX creation, editing, and analysis

A `.pptx` is a ZIP archive of XML files. Choose your approach by task:

| Task | Approach |
|---|---|
| **Create** a new deck | Write a `pptxgenjs` script — see gotchas below |
| **Edit** an existing deck, or build from a template | unzip → edit `ppt/slides/slideN.xml` → zip |
| **Read** content | `markitdown deck.pptx` (one block per slide under `<!-- Slide number: N -->` markers); visual grid: `python scripts/thumbnail.py deck.pptx` |

## Scripts

Paths are relative to this skill's directory. Everything else is plain Python, `node`, or shell.

| Script | What it does |
|---|---|
| `scripts/thumbnail.py deck.pptx [prefix]` | Labeled grid of every slide, for picking template layouts. `.pptx` only. Pass `prefix` — it defaults to `thumbnails`, which overwrites the grids of any other deck done in the same directory |
| `scripts/add_slide.py unpacked/ slide2.xml [--after slideN.xml]` | Duplicate a slide (or a `slideLayoutN.xml`) with all the package bookkeeping. Also takes a `.pptx` directly with `-o out.pptx` |
| `scripts/clean.py unpacked/` | Delete slides, media, and rels no longer referenced. Run **after** `<p:sldIdLst>` is final |
| `scripts/office/validate.py deck.pptx [--original src.pptx]` | Schema, relationship, content-type, chart and slide checks; each failure names its fix. Pass `--original` for any template-derived deck — it baselines the schema checks against the template, so the template's own XSD errors don't read as yours |
| `scripts/office/soffice.py --headless --convert-to pdf deck.pptx` | LibreOffice wrapper — bare `soffice` hangs in this sandbox |

## Creating with pptxgenjs — gotchas

`pptxgenjs` is preinstalled — do not run `npm install` first; write the script and `require('pptxgenjs')` directly. Only if that require fails: `npm install pptxgenjs`. The model knows the API; these are the footguns:

- **Set `pres.layout` before adding slides.** The default canvas is `LAYOUT_16x9` = **10" × 5.625"**, not 13.3" wide. Coordinates past the edge are written, not clamped — the shape just isn't on the slide. (`LAYOUT_WIDE` is 13.3" × 7.5".)
- **Hex colors: never `#`, never 8 digits.** `color: "FF0000"`. Both `"#FF0000"` and alpha baked into the hex (`"00000020"`) **corrupt the file**. For translucency: `transparency: 0-100` on fills and images, `opacity: 0.0-1.0` on shadows — each is silently ignored on the other.
- **pptxgenjs mutates option objects in place** (converts values to EMU on first use). Never share one `shadow`/options object across two `add*` calls — build a fresh object each time.
- **Shadow `offset` must be ≥ 0** — a negative offset corrupts the file. To cast a shadow upward, use `angle: 270` with a positive offset.
- **`letterSpacing` is silently ignored** — the real option is `charSpacing`.
- **Lists:** `bullet: true` on each item, never a literal `•` (renders double bullets). Set `breakLine: true` on every array item except the last. Space bulleted paragraphs with `paraSpaceAfter`, not `lineSpacing` (huge gaps).
- **One `new pptxgen()` per output file** — never reuse an instance.
- **`rectRadius` only works on `ROUNDED_RECTANGLE`**, not `RECTANGLE`.
- **Gradient fills aren't supported** — use a gradient image as the background instead.
- **Text boxes have built-in internal padding** — set `margin: 0` whenever text must align with a shape, line, or icon at the same x.
- **Speaker notes go in `slide.addNotes("...")`** (plain text, once per slide), never in a text box on the slide.
- **Keep charts native.** Use `addChart()` for everything PowerPoint can chart (pass an array of `{type, data, options}` for combos). For PowerPoint-native features the library doesn't expose (trendlines, error bars), compute the extra series yourself or post-process the generated OOXML — do not fall back to a rendered image. Only chart types PowerPoint has no native form for (Sankey, network, chord) go in as images.
- **Default charts render bare** — no title, no data labels, dated palette. Set `showTitle` + `title`, `showValue: true` + `dataLabelPosition`, `chartColors: [...]` from your palette, and quiet the frame (`catAxisLabelColor`/`valAxisLabelColor`, `valGridLine: { color, size }`, `catGridLine: { style: "none" }`, `showLegend: false` for a single series).
- **On a stacked bar or column chart, `dataLabelPosition` must be `ctr`, `inEnd`, or `inBase`.** `outEnd` **corrupts the file**.
- **A combo series using `secondaryValAxis`/`secondaryCatAxis` needs both `valAxes` and `catAxes` on the chart options, two entries each.** Without them pptxgenjs writes axis *ids* it never declares, and PowerPoint **discards that chart** and reports the file as corrupt. Supplying only `valAxes` is not enough.
- **After `writeFile()`, run `python scripts/office/validate.py deck.pptx`.** It reports the two chart faults above and the slide-XML defects PowerPoint refuses, and names the fix for each. Fix them in your generator, not by hand-editing the packed XML.
- **Never reorder the children of `<p:presentation>`.** pptxgenjs writes `<p:notesMasterIdLst>` right after `<p:sldIdLst>` and points both masters at one theme part. PowerPoint reads that happily — move the element and the same deck becomes unopenable.
- **Icons:** render `react-icons` to SVG (`ReactDOMServer.renderToStaticMarkup`), rasterize with `sharp` at ≥256px, and insert via `addImage({ data: "image/png;base64," + buf.toString("base64") })` — the `image/png;base64,` prefix is required (`react-icons`, `react`, `react-dom`, and `sharp` are preinstalled — `npm install react-icons react react-dom sharp` only if a require fails).

## Editing existing decks and templates

Pick layouts first: `python scripts/thumbnail.py template.pptx template-thumbs` writes a labeled grid of every slide and prints the file(s) it created — `template-thumbs.jpg`, split into `template-thumbs-N.jpg` past 12 slides. **Always pass that second argument, named after the deck.** It defaults to `thumbnails`, so two decks thumbnailed in one directory silently overwrite each other's grids — the first deck's are simply gone (template analysis only — visual QA needs the full-resolution renders from [Converting to Images](#converting-to-images); it only accepts `.pptx`, so copy a `.potx` to a `.pptx` name first). Use it with `markitdown` to map each content section onto a template slide, and vary the layouts — don't put every section on the same title-and-bullets slide.

```bash
python3 -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall('unpacked')" deck.pptx
python scripts/add_slide.py unpacked/ slide2.xml --after slide2.xml   # duplicate a slide (or slideLayoutN.xml); prints the new slide's path
# reorder / delete slides = edit <p:sldIdLst> in ppt/presentation.xml
python scripts/clean.py unpacked/                                     # after deletions: removes orphaned slides, media, rels
# edit slide content in ppt/slides/slideN.xml
(cd unpacked && rm -f ../out.pptx && zip -Xr ../out.pptx .)           # zip from INSIDE the dir; rm first or deleted parts survive
python scripts/office/validate.py out.pptx --original deck.pptx
```

- **Do all structural work — add, delete, reorder — before editing any slide's content.** `add_slide.py` copies a slide file verbatim, so duplicating after you edit clones the edited content; and `clean.py` deletes any slide missing from `<p:sldIdLst>`, including one you just wrote.
- **Never copy a slide file by hand** — `add_slide.py` does every registration a new slide needs and reports what it made (`Created ppt/slides/slide17.xml from slide2.xml`). It also works directly on a file: `add_slide.py deck.pptx slide2.xml -o out.pptx` — **pass `-o`, or it rewrites the input deck in place.** A duplicated slide still *references* its source's chart/SmartArt/embedded-object parts rather than cloning them, so editing one slide's chart changes the other's.
- **If you use `python-pptx`**, three things it won't do: duplicate a slide (its only entry point is `add_slide(layout)`), preserve formatting through `text_frame.text = "..."` (that collapses the paragraph to a single unstyled run — assign `run.text` instead), or read the SVG/EMF most template art uses (`add_picture` raises `UnidentifiedImageError`).
- Legacy `.ppt` must be converted first: `python scripts/office/soffice.py --headless --convert-to pptx file.ppt`. `.potx` templates unpack and pack identically — keep the `.potx` extension on the output.
- To reuse a template icon or image, duplicate a slide or layout that already contains it.

When filling in a template:

- If you script an XML transform, parse with `defusedxml.minidom` — round-tripping OOXML through `xml.etree.ElementTree` rewrites namespace prefixes and corrupts the deck.
- **Template slots ≠ source items.** If the template shows 4 team members and you have 3, delete the 4th member's entire group (image + text boxes), not just its text — then check for orphaned visuals in QA.
- One `<a:p>` per list item — never concatenate items into a single paragraph. Copy the sibling `<a:pPr>` to preserve spacing, and put `b="1"` on the `<a:rPr>` of titles, section headers, and inline labels (`Status:`, `Owner:`).
- Let bullets inherit from the layout; only add `<a:buChar>`, `<a:buAutoNum>` (numbered), or `<a:buNone>` to override — never a literal `•` in the text.
- Text with leading or trailing spaces needs `xml:space="preserve"` on its `<a:t>`.

## Design Ideas

**Don't create boring slides** — the full craft (palette, per-slide variety,
typography, spacing, the Avoid list) lives in `references/design-ideas.md`;
read it before designing a deck from scratch. On the skeleton-pipeline path
the design comes from the user's `design.md` (Input contract below) — the
reference applies when you author the palette yourself.

## QA (Required)

Your first render usually has a few real issues — overlaps, overflow, misalignment. Find and fix those, re-render only the slides you changed, and stop.

### Content QA

```bash
markitdown output.pptx
```

Check for missing content, typos, wrong order.

**When using templates, check for leftover placeholder text:**

```bash
markitdown output.pptx | grep -iE "\bx{3,}\b|lorem|ipsum|\bTODO|\[insert|this.*(page|slide).*layout"
```

If grep returns results, fix them before declaring success.

### File QA (required)

```bash
python scripts/office/validate.py output.pptx                      # built from scratch
python scripts/office/validate.py output.pptx --original src.pptx  # built from a template
```

**If the deck came from a template, always pass `--original`.** A template may itself
contain parts the XSD rejects, so a bare run can report failures you never caused — and
a genuine regression can hide among them. `--original` baselines
the schema and slide checks against the template, suppressing errors it already had.
The structural checks — relationships, content types, charts — ignore `--original` and
report template-inherited problems either way, so read those on their own merits.

pptxgenjs emits chart XML PowerPoint refuses to open, and every other tool
accepts: python-pptx opens those decks, LibreOffice renders them, the XSD
passes them. Every failure names its fix. Fix it in the generator and rebuild.

### Visual QA

Convert the slides to images (see [Converting to Images](#converting-to-images)) and inspect every one. After staring at the generating code you tend to see what you expect rather than what rendered, so look at the images fresh (a subagent works well for this if you have one). User-visible defects to look for:

- **Text overflow or text cut off at a box or slide boundary — check this first.** It is the most common defect and always user-visible. (For a font the previewer renders unreliably per `references/design-ideas.md` Typography, the preview is approximate: trust the ~10% slack you left, not its apparent fit.)
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Body text runs below the 18 pt floor (`D.body_size`) — the PPTX twin of the 25 px HTML body floor
- Template decoration mispositioned after text replacement — e.g., a title underline positioned for one line, but the replaced title wrapped to two
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

## Converting to Images

Convert presentations to individual slide images for visual inspection:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 output.pdf slide
ls -1 "$PWD"/slide-*.jpg
```

**Pass the absolute paths printed above directly to the view tool.** The `rm` clears stale images from prior runs. `pdftoppm` zero-pads based on page count: `slide-1.jpg` for decks under 10 pages, `slide-01.jpg` for 10-99, `slide-001.jpg` for 100+.

**After fixes, rerun all four commands above** — the PDF must be regenerated from the edited `.pptx` before `pdftoppm` can reflect your changes.

## Dependencies

`pptxgenjs` (npm, preinstalled — install only if `require('pptxgenjs')` fails) · `markitdown[pptx]`, `Pillow`, `defusedxml`, `lxml` (pip — text dump, thumbnail, clean, validate) · LibreOffice (`soffice`, auto-configured for sandboxed environments via `scripts/office/soffice.py`) · `pdftoppm` (Poppler)

## Skeleton to deck (this project's pipeline)

When the input is a presentation skeleton (skeleton.yaml, from the presentation-skeleton
skill) plus a design.md, this is the main use of the skill. The pipeline below feeds the
QA sections above; the original workflow covers ad-hoc .pptx work.

### Input contract

- `*.skeleton.yaml` — schema v1.1 (meta: title, tone, anim_role, target; slides: id,
  title, layout, blocks, figure, anim, notes). Parse it with `scripts/yaml2json.py`;
  a parse error is a bad skeleton, not a rendering problem — send it back.
- **Sub-bullets:** a line indented with exactly two leading spaces in a `bullet` block is a
  sub-item — second level (larger indent, smaller en-dash marker); other indentation is undefined (skeleton-format convention).
- `design.md` next to the skeleton (or a path the user gives). Extract the tokens into a
  `tokens.json` with `mapping_notes` — the repo keeps the contract example:
  `evals/prototypes/pptx-engines/design-glitch.tokens.json`. No design.md → the
  generator's academic-light defaults (or the palette table in
  `references/design-ideas.md`, if designing from scratch).
- **Static only.** This render target ignores `anim` entirely (no PPTX animation —
  stability is the bar). A drawable figure (kind `diagram` / `chart` / `circuit`) is
  **authored by you** and embedded as a PNG — see Figures below. A placeholder panel
  (figfill + figure.prompt text) is a last resort: kind `image` (photos you cannot
  invent) or an explicit user opt-out. A deck whose drawable figures are all
  placeholders is a failed deck.

### Build

```bash
python3 scripts/yaml2json.py <name>.skeleton.yaml work/skel.json
node scripts/gen_template.js work/skel.json [work/tokens.json] work/deck.pptx
```

`scripts/gen_template.js` is the seed generator (token-driven; defaults = academic-light).
When the design or a layout needs something the seed lacks, extend the generator —
never hand-edit the packed XML (see File QA).

### Figures

Drawable figures (kind `diagram` / `chart` / `circuit`) are produced by the
**deck-animation skill** — follow it for the authoring methodology (settled state,
semantic element ids, factual accuracy, clearance/plot rules) and for its QA loop. It
delivers, per figure: `fig-<id>.svg` (settled, semantic ids), `fig-<id>.manifest.json`,
`fig-<id>.tl.js` (GSAP fragment — **not used by this target**), and `fig-<id>.png`
(settled raster). This target's job is the PPTX mechanics only:

1. Embed the settled PNG via the per-slide `figure_images` tokens mapping:
   `"figure_images": [{ "id": "<slide id>", "file": "assets/fig-<id>.png" }]` — checked
   before the kind-level `figure_image`. The seed sizes each image from its real PNG
   dimensions and letterboxes it onto the figfill panel.
2. Rasterize only if you need to re-derive the PNG from the SVG:
   `chromium --headless --screenshot=fig-<id>.png --window-size=<W>,<H> fig-<id>.svg`.

Placeholder panel (figfill + prompt text) remains the last resort: kind `image` (photos)
or an explicit user opt-out. A deck whose drawable figures are all placeholders is a
failed deck.

### Tokens

`bg, title, body, muted, accent, header_text, figfill, figline, figtext, cardfill,
row_alt, font, body_font (optional — body/tables face, defaults to font), title_size,
body_size, caption_size, table_size` + optional factura layers `overlay_image`
(whole-slide texture PNG), `ghost_title` (pre-blended ghost offset/colors — PPTX has
no text-shadow or blend modes), `figure_image` (PNG for a figure zone). `overlay_image`
and `figure_image` are paths relative to the tokens file's directory. Factura in PPTX
= static pre-rendered PNGs, never CSS.

### Findings from the test stand (on top of the gotchas above)

- **Dark themes (P0):** explicit background on every slide; explicit fill on EVERY table
  row and explicit text color on EVERY cell — the default cell text color is black and
  invisible on dark fills (G-1). Same discipline for figure zones: figfill panel +
  figline stroke + figtext color, all from tokens.
- **Dense tables (P0):** monospace fonts with tall line metrics (JetBrains Mono) push
  18 pt rows to ~0.65 in — a 10-row table overflows the slide. Use a compact-metric
  mono (PT Mono, ~0.57 in/row). The body floor is 18 pt: split the table, never shrink
  the font (G-2).
- **Cell margins:** defaults are ~0.1 in vertical → set `margin: 0.05` on tables (G-3).
- **Font coverage:** check Cyrillic coverage of the DS font BEFORE the run — a Latin-only
  display font (e.g. Share Tech Mono) must be replaced; record the choice in `mapping_notes`.
- **Letterbox seams:** an image in a figure zone needs the figfill panel behind it, or the
  slide background shows as strips (G-4).
- **Full resolution:** inspect renders at full resolution — 96 dpi chat previews ghost and
  double; that is a compression artifact, not a deck defect.
- **Block-scalar text (found in the first two runs):** skeleton text fields come from YAML
  block scalars and keep a trailing newline — an untrimmed value renders a stray empty
  bullet. The seed trims; keep trimming in any generator you extend.
- **Merged paragraphs (found in the noir run):** pptxgenjs merges consecutive array items
  into one paragraph unless each carries `bullet` or `breakLine` — no-bullet lines flowed
  together until `breakLine: true` was set on all-but-last.

### Output and artifacts

The deck ships as **deck.pptx AND deck.pdf** (the PDF is the first step of Converting to
Images — keep it as an artifact). Render everything with `scripts/render.sh`:

```bash
bash scripts/render.sh work/deck.pptx <results_dir>   # PDF + per-slide PNGs (150 dpi) + contact-sheet.png
```

- Results go to `evals/results/<run>/` (or the user's directory when working outside evals).
  Working files (parsed JSON, generator copy) go in a `work/` subfolder of that results
  dir — the repo root stays clean. **Figure assets from the deck-animation skill go in
  the run's `assets/`** (the tokens reference them by relative path — they are run
  artifacts, not transients).
- **Never modify the input skeleton to fix a rendering problem** — the skeleton is the
  shared test input; fix in the generator, and only trim the skeleton's own text when it
  genuinely overflows its budget (and say so in the report).
- **Review loop = the QA sections above:** visual QA (fresh eyes; a subagent works well) →
  fix in the generator or skeleton → rebuild → re-render only changed slides; ≤3 rounds,
  then report remaining defects to the user.
- **Archive before fixing:** a broken or failed render state is copied to `archive/`
  inside the run's results dir BEFORE fixing it in place — never overwrite the evidence
  (AGENTS.md).
