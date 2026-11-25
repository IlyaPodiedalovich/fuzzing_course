#!/usr/bin/env node
// Seed generator: skeleton (JSON, from yaml2json.py) + tokens.json -> deck.pptx.
// Token-driven, defaults = academic-light. Extend it when a layout needs more —
// never hand-edit the packed XML.
// usage: node gen_template.js <skeleton.json> [tokens.json] <out.pptx>
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

// defaults = academic-light theme; tokens.json overrides
const D = {
  bg: "FFFFFF", title: "0F1E3D", body: "22303F", accent: "2563EB",
  figfill: "EEF2F7", figline: "B9C6D6", figtext: "5A6B7F", muted: "5A6B7F",
  font: "PT Sans", body_font: null, title_size: 32, body_size: 18, caption_size: 12,
  header_text: "FFFFFF", row_alt: null,
};
let FONT = D.font;
let BFONT = D.font; // body/table/formula face (token body_font; defaults to the display font)

const geo = () => ({
    title: { x: 0.6, y: 0.5, w: 12.133, h: 0.9 },
    text: (l) => l === "content-right" ? { x: 0.6, y: 1.7, w: 6.4, h: 5.0 }
      : l === "content-left" ? { x: 6.3, y: 1.7, w: 6.43, h: 5.0 }
      : { x: 0.6, y: 1.7, w: 12.133, h: 5.0 },
    fig: (l) => l === "content-right" ? { x: 7.3, y: 1.7, w: 5.43, h: 4.6 }
      : l === "diagram" ? { x: 0.6, y: 1.7, w: 12.133, h: 4.6 }
      : { x: 0.6, y: 1.7, w: 5.43, h: 4.6 },
    grid: (i) => ({ x: 0.6 + i * (2.246 + 0.25), y: 1.7, w: 2.246, h: 4.6 }),
  });

function figPlaceholder(slide, g, figure) {
  slide.addShape("roundRect", {
    x: g.x, y: g.y, w: g.w, h: g.h, rectRadius: 0.08,
    fill: { color: D.figfill }, line: { color: D.figline, width: 1 },
  });
  slide.addText(
    [
      { text: "FIG", options: { bold: true, breakLine: true, fontFace: FONT } },
      { text: trimEnd(figure.prompt), options: { breakLine: true } },
      { text: trimEnd(figure.caption || ""), options: { italic: true } },
    ],
    {
      x: g.x + 0.15, y: g.y + 0.15, w: g.w - 0.3, h: g.h - 0.3,
      fontFace: BFONT, fontSize: D.caption_size, color: D.figtext, valign: "middle",
    }
  );
}

function bullets(slide, box, blocks, opts = {}) {
  const { paraSpaceAfter = 10, noBullet = false } = opts;
  // one <a:p> per line: block scalars keep a trailing newline, and one item with
  // internal newlines renders as a single paragraph (one bullet, stray empty one)
  const items = [];
  for (const b of blocks.filter((b) => b.type === "bullet" || b.type === "text")) {
    for (const raw of b.text.split(/\r?\n/)) {
      const line = raw.trim();
      if (!line.length) continue;
      // an indented line (exactly two leading spaces) in a bullet block is a
      // sub-item: larger indent + smaller marker (skeleton-format convention,
      // retro-2 ticket 03); in noBullet mode lines are paragraphs, not bullets
      const isSub = b.type === "bullet" && raw.startsWith("  ") && !raw.startsWith("   ");
      items.push({
        text: line,
        options: noBullet
          ? { color: D.body }
          : isSub
            ? { bullet: { code: "2013", indent: 30 }, color: D.body }
            : { bullet: { code: "2022", indent: 14 }, color: D.body },
      });
    }
  }
  if (!items.length) return;
  // pptxgenjs merges consecutive array items into one <a:p> unless the item has
  // bullet or breakLine (found in noir run: no-bullet lines flowed together)
  items.forEach((it, i) => { if (i < items.length - 1) it.options.breakLine = true; });
  slide.addText(items, {
    ...box, fontFace: BFONT, fontSize: D.body_size, color: D.body,
    paraSpaceAfter, valign: "top",
  });
}

// rough rendered height (inches) of text paragraphs at body_size in a box of widthIn:
// ~8 chars/in for 18pt Calibri-class metrics, 0.30in per line, 0.14in per paragraph gap.
function estTextH(texts, widthIn) {
  // per-line paragraphs (same split as bullets()); ~8 chars/in at 18pt Calibri class
  let lines = 0, paras = 0;
  for (const t of texts) {
    for (const l of t.split(/\r?\n/).map((x) => x.trim()).filter((x) => x.length)) {
      lines += Math.max(1, Math.ceil([...l].length / Math.max(10, widthIn * 8)));
      paras++;
    }
  }
  return lines * 0.3 + (paras - 1) * 0.14;
}

function formula(slide, box, f) {
  slide.addText(
    [
      { text: trimEnd(f.text), options: { bold: true, breakLine: !!f.caption } },
      ...(f.caption ? [{ text: trimEnd(f.caption), options: { italic: true, fontSize: D.caption_size, color: D.figtext } }] : []),
    ],
    { ...box, fontFace: BFONT, fontSize: D.body_size, color: D.accent, valign: "top" }
  );
}

const trimEnd = (v) => (typeof v === "string" ? v.replace(/\s+$/g, "") : v); // block scalars keep a trailing newline

function table(slide, box, t, colW) {
  const rows = [
    t.columns.map((c) => ({
      text: c, options: { bold: true, color: D.header_text, fill: { color: D.accent } },
    })),
    ...t.rows.map((r, i) => r.map((cell) => ({
      text: cell,
      // explicit fill on EVERY row: default table styles are light — invisible on dark themes
      options: { color: D.body, fill: { color: i % 2 ? (D.row_alt || D.bg) : D.bg } },
    }))),
  ];
  slide.addTable(rows, {
    ...box,
    fontFace: BFONT, fontSize: D.table_size || D.body_size,
    colW: colW || (t.columns.length === 4 ? [2.3, 4.1, 2.7, 3.033]
      : Array(t.columns.length).fill(+(12.133 / t.columns.length).toFixed(3))),
    rowH: 0.42, // dense-table fix: natural 1-line row at 18pt ≈ 0.41in (glitch-run finding)
    margin: 0.05, // default cell margins (~0.1in v) push rows to ~0.65in — a 10-row 18pt table overflows (found in glitch run)
    border: { type: "solid", color: D.figline, pt: 0.75 },
    valign: "middle",
  });
}

function cards(slide, blocks, layout) {
  blocks.forEach((c, k) => {
    // cards layout = 2-4 wider columns; grid-5 = the fixed 5-column grid
    const g = layout === "cards"
      ? (() => {
          const n = Math.min(4, Math.max(2, blocks.length));
          const w = (12.133 - (n - 1) * 0.25) / n;
          return { x: 0.6 + k * (w + 0.25), y: 1.7, w, h: 4.6 };
        })()
      : geo().grid(k);
    slide.addShape("roundRect", {
      ...g, rectRadius: 0.06, fill: { color: D.figfill },
      line: { color: D.figline, width: 1 },
    });
    slide.addText(
      [
        { text: trimEnd(c.title), options: { bold: true, breakLine: true } },
        { text: trimEnd(c.body), options: {} },
      ],
      { ...g, x: g.x + 0.1, w: g.w - 0.2, fontFace: BFONT, fontSize: D.body_size, color: D.body, valign: "middle" }
    );
  });
}

let TOKDIR = "."; // image token paths resolve against the tokens file dir

// PNG pixel size from the IHDR (for aspect-fit into the figure zone)
function pngSize(p) {
  const b = fs.readFileSync(p);
  return [b.readUInt32BE(16), b.readUInt32BE(20)];
}

// Figure zone: per-slide image (tokens.figure_images) -> kind image (figure_image)
// -> placeholder panel. Keeps the figfill panel behind the image (seamless letterbox).
function drawFigure(slide, g, figure, slideId) {
  let file = null;
  const per = (D.figure_images || []).find((m) => m.id === slideId);
  if (per) file = per.file;
  else if (D.figure_image && figure.kind === D.figure_image.match_kind) file = D.figure_image.file;
  if (file) {
    const fp = path.join(TOKDIR, file);
    const [pw, ph] = pngSize(fp);
    let iw = g.w, ih = (iw * ph) / pw;
    if (ih > g.h) { ih = g.h; iw = (ih * pw) / ph; }
    slide.addShape("rect", { x: g.x, y: g.y, w: g.w, h: g.h, fill: { color: D.figfill } });
    slide.addImage({ path: fp, x: g.x + (g.w - iw) / 2, y: g.y + (g.h - ih) / 2, w: iw, h: ih });
    slide.addShape("rect", { x: g.x, y: g.y, w: g.w, h: g.h, line: { color: D.figline, width: 2.5 } });
  } else {
    figPlaceholder(slide, g, figure);
  }
}

async function main() {
  const args = process.argv.slice(2);
  const [skPath, tokPath, outPath] = args.length === 3 ? args : [args[0], null, args[1]];
  if (tokPath) {
    Object.assign(D, JSON.parse(fs.readFileSync(tokPath, "utf8")));
    TOKDIR = path.dirname(path.resolve(tokPath));
  }
  FONT = D.font;
  BFONT = D.body_font || D.font;
  const sk = JSON.parse(fs.readFileSync(skPath, "utf8"));
  const pres = new pptxgen();
  pres.defineLayout({ name: "W16x9", width: 13.333, height: 7.5 });
  pres.layout = "W16x9";
  const G = geo();

  sk.slides.forEach((sl, idx) => {
    const slide = pres.addSlide();
    slide.background = { color: D.bg };
    const gt = D.ghost_title;
    if (gt) {
      // chromatic-aberration ghosts (pre-blended colors; PPTX has no text-shadow/blend)
      slide.addText(sl.title, {
        ...G.title, x: G.title.x - gt.dx_in, fontFace: FONT, fontSize: D.title_size, bold: true, color: gt.cyan, valign: "middle",
      });
      slide.addText(sl.title, {
        ...G.title, x: G.title.x + gt.dx_in, fontFace: FONT, fontSize: D.title_size, bold: true, color: gt.red, valign: "middle",
      });
    }
    if (sl.layout !== "section") {
      slide.addText(sl.title, {
        ...G.title, fontFace: FONT, fontSize: D.title_size, bold: true, color: D.title, valign: "middle",
      });
    }
    slide.addText(`${idx + 1} / ${sk.slides.length}`, {
      x: 11.6, y: 7.05, w: 1.1, h: 0.3, fontFace: FONT, fontSize: D.caption_size, color: D.figtext, align: "right",
    });
    if (sl.layout === "section") {
      // title slide: centered title + centered muted subtitle (no bullet)
      slide.addText(sl.title, {
        ...G.title, fontFace: FONT, fontSize: D.title_size, bold: true, color: D.title,
        align: "center", valign: "middle",
      });
      const sub = sl.blocks.filter((b) => b.type === "text").map((b) => b.text).join("\n");
      if (sub) {
        slide.addText(sub, {
          x: 1.5, y: 3.5, w: 10.333, h: 0.7,
          fontFace: BFONT, fontSize: D.body_size, color: D.muted, align: "center", valign: "top",
        });
      }
    } else if (sl.layout === "table") {
      // full-width dense table: colW tuned per-column (longest cells col1/col4/col3),
      // starts at 1.65" so 2-line rows still clear the 6.9" content-max line
      table(slide, { x: 0.6, y: 1.65, w: 12.133, h: 5.2 },
            sl.blocks.find((b) => b.type === "table"), [2.9, 3.1, 3.2, 2.933]);
    } else if (sl.layout === "grid-5") {
      cards(slide, sl.blocks, "grid-5");
    } else if (sl.layout === "cards") {
      cards(slide, sl.blocks, "cards");
    } else {
      const tb = G.text(sl.layout);
      const hasTable = sl.blocks.some((b) => b.type === "table");
      if (hasTable) {
        // content slide with a table block: bullets full-width on top, bottom row =
        // table (left) + figure panel (right) — the side column can't stack both
        bullets(slide, { x: 0.6, y: 1.65, w: 12.133, h: 2.7 }, sl.blocks, { paraSpaceAfter: 6, noBullet: true });
        const ty = 4.62, th = 6.9 - ty;
        const tbl = sl.blocks.find((b) => b.type === "table");
        table(slide, { x: 0.6, y: ty, w: 8.2, h: th }, tbl,
              Array(tbl.columns.length).fill(+(8.2 / tbl.columns.length).toFixed(3)));
        if (sl.figure) drawFigure(slide, { x: 9.05, y: ty, w: 3.683, h: th }, sl.figure, sl.id);
      } else if ((sl.layout === "full" || sl.layout === "diagram") && sl.figure) {
        // text on top, figure panel below (the seed's fixed zones would overlap)
        bullets(slide, tb, sl.blocks);
        const texts = sl.blocks.filter((b) => b.type === "text" || b.type === "bullet").map((b) => b.text);
        const th = Math.min(tb.h, Math.max(1.4, estTextH(texts, tb.w)));
        const figY = Math.min(6.9 - 2.2, tb.y + th + 0.3);
        drawFigure(slide, { x: 0.6, y: figY, w: 12.133, h: 6.9 - figY }, sl.figure, sl.id);
      } else {
        const f = sl.blocks.find((b) => b.type === "formula");
        if (f) {
          const fbox = { ...tb, h: 1.1 };
          formula(slide, fbox, f);
          bullets(slide, { ...tb, y: tb.y + 1.15, h: tb.h - 1.15 }, sl.blocks);
        } else {
          bullets(slide, tb, sl.blocks);
        }
        if (sl.figure) drawFigure(slide, G.fig(sl.layout), sl.figure, sl.id);
      }
    }
    if (sl.notes) slide.addNotes(sl.notes);
    if (D.overlay_image) {
      // pre-rendered texture over the whole slide (added last = topmost)
      slide.addImage({ path: path.join(TOKDIR, D.overlay_image), x: 0, y: 0, w: 13.333, h: 7.5 });
    }
  });

  await pres.writeFile({ fileName: outPath });
  console.log("wrote", outPath);
}

main().catch((e) => { console.error(e); process.exit(1); });
