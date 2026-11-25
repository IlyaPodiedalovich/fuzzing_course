/* deck-html runtime (D2) — inlined by gen_deck.py after the FIGS map.
 *
 * Model: per slide, TWO independent paused timelines — the text wave and the
 * figure fragment timeline — never nested. (This vendored GSAP build collapses
 * a parent timeline's duration to 0 when a child timeline is added — verified
 * in evals; side-by-side keeps the seek math explicit and R3-stable.)
 *
 * Sync: the figure starts after the wave (offset = waveDur + 0.3 s); the slide
 * total = max(waveDur, offset + figDur); a capture ?t=progress maps to
 * tSeconds = t * total and both timelines are seeked by absolute time.
 *
 * Determinism: no random, no Date.now. Loop = deck-level restart (T-14),
 * figure slides only, cleared on navigation / capture / print.
 */
(function () {
  "use strict";
  const N = window.__N__;
  const stage = document.querySelector(".deck-stage");
  const slides = Array.from(document.querySelectorAll(".slide"));
  let idx = -1;
  let loopTimer = null;
  let figTimer = null;
  let frozen = false; // capture mode (?t=) or print

  function clamp01(v) { return Math.max(0, Math.min(1, v)); }

  function fitStage() {
    const p = new URLSearchParams(location.search);
    if (p.has("capture") || frozen) { stage.style.transform = "none"; return; }
    let s = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    if (Math.abs(s - 1) < 0.02) s = 1; // 1:1 capture context
    const x = (window.innerWidth - 1920 * s) / 2;
    const y = (window.innerHeight - 1080 * s) / 2;
    stage.style.transform = "translate(" + x + "px," + y + "px) scale(" + s + ")";
  }

  const built = {}; // i -> {wave, fig, waveDur, figDur, offset, total}
  function build(i) {
    if (built[i]) return built[i];
    const el = slides[i];
    const revs = Array.from(el.querySelectorAll(".reveal"));
    // Group .reveal items by data-beat (skeleton `beat: bN` per block),
    // preserving DOM order of first appearance. One group = one wave;
    // without beat fields this degenerates to the old single cascade.
    const groups = [];
    revs.forEach(function (r) {
      const key = r.dataset.beat || "b0";
      let g = null;
      for (const gg of groups) if (gg.key === key) { g = gg; break; }
      if (!g) { g = { key: key, items: [] }; groups.push(g); }
      g.items.push(r);
    });
    // FX vocabulary (skeleton block field `fx:`, data-fx in DOM).
    // NOTE: this vendored GSAP 3.14.2 build does NOT interpolate clip-path
    // mid-tween (verified: value stays at `from` until end) — so mask/type
    // never use clipPath. mask = translateX wipe inside .fxwipe (overflow
    // hidden wrapper, gen_deck); type = per-line print spans (gen_deck).
    //  print   — instant console-line appearance (opacity 0->1, 0.08s)
    //  mask    — slide-in from the right behind an overflow mask (0.5s)
    //  type    — legacy alias of mask if ever emitted as a single element
    //  flicker — stepped opacity, CRT flicker-in (0.4s steps(6))
    //  fade-up — legacy default (opacity + y:28, 0.45s)
    const DUR = { "print": 0.08, "mask": 0.5, "type": 0.5,
                  "flicker": 0.4, "fade-up": 0.45 };
    function fxOf(r) { return r.dataset.fx || "fade-up"; }
    const wave = gsap.timeline({ paused: true });
    let t = 0;
    groups.forEach(function (g, gi) {
      if (gi > 0) t += 0.45; // pause between beats
      let maxD = 0;
      g.items.forEach(function (r, k) {
        const fx = fxOf(r);
        const d = DUR[fx] || DUR["fade-up"];
        if (d > maxD) maxD = d;
        const start = t + k * 0.12;
        if (fx === "print") {
          wave.fromTo(r, { opacity: 0 }, { opacity: 1, duration: d }, start);
        } else if (fx === "mask" || fx === "type") {
          // x-wipe: element slides in from the right; .fxwipe clips it
          wave.fromTo(r, { x: "100%" }, { x: "0%", duration: d,
                      ease: "power2.out" }, start);
        } else if (fx === "flicker") {
          wave.fromTo(r, { opacity: 0 },
                      { opacity: 1, duration: d, ease: "steps(6)" }, start);
        } else {
          wave.fromTo(r, { opacity: 0, y: 28 },
                      { opacity: 1, y: 0, duration: d, ease: "power2.out" },
                      start);
        }
      });
      t += maxD + (g.items.length - 1) * 0.12;
    });
    const waveDur = groups.length ? t : 0;
    let fig = null;
    let figDur = 0;
    const fid = el.id;
    if (window.FIGS && window.FIGS[fid] && typeof window.FIGS[fid] === "function") {
      fig = window.FIGS[fid](gsap); // paused fragment timeline (T-5 inside it)
      figDur = fig.duration();
    }
    const offset = waveDur + 0.3;
    const total = Math.max(waveDur, offset + figDur);
    built[i] = { wave: wave, fig: fig, waveDur: waveDur, figDur: figDur,
                 offset: offset, total: total };
    return built[i];
  }

  function seekSlide(i, tSeconds) {
    const b = build(i);
    if (b.waveDur > 0) b.wave.progress(clamp01(tSeconds / b.waveDur));
    if (b.fig) b.fig.progress(clamp01((tSeconds - b.offset) / b.figDur));
  }

  function killTimers() {
    if (loopTimer) { clearTimeout(loopTimer); loopTimer = null; }
    if (figTimer) { clearTimeout(figTimer); figTimer = null; }
  }

  function playSlide(i) {
    killTimers();
    const b = build(i);
    b.wave.progress(0).play();
    if (b.fig) {
      b.fig.progress(0);
      figTimer = setTimeout(function () {
        figTimer = null;
        if (!frozen && i === idx) b.fig.play();
      }, b.offset * 1000);
      b.fig.eventCallback("onComplete", function () {
        if (frozen || i !== idx) return;
        loopTimer = setTimeout(function () {
          if (!frozen && i === idx) playSlide(i); // T-14: hold, then replay
        }, 1500);
      });
    }
  }

  function show(i) {
    killTimers();
    idx = Math.max(0, Math.min(N - 1, i));
    slides.forEach((s, k) => s.classList.toggle("active", k === idx));
    if (window.gsap && !frozen) playSlide(idx);
  }

  function freezeAll() {
    frozen = true;
    killTimers();
    Object.keys(built).forEach(function (k) {
      const b = built[k];
      b.wave.pause();
      if (b.waveDur > 0) b.wave.progress(1);
      if (b.fig) { b.fig.pause(); b.fig.progress(1); }
    });
  }

  // ?audit=1 — text collision / overflow gate (F-H3; scripts/text_audit.py).
  // Every slide is forced to its SETTLED pose first (wave + figure seeked to
  // 1 — the state F-P2 prints, so in-flight animation transforms can't skew
  // the rects), then every VISIBLE-in-settle leaf text rect is measured.
  // (Settle-invisible elements are skipped: inline visibility:hidden — what
  // GSAP autoAlpha and base-SVG state groups set — on the element or a
  // non-slide ancestor, or computed opacity < 0.05. Slide-stack hiddenness is
  // class-based on the section and deliberately NOT filtered: stacked slides
  // keep a valid layout and must be audited.)
  //   OVERFLOW — a text leaf outside the 1920x1080 stage
  //   OVERLAP  — two non-nested text leaves intersect by more than 120 px^2,
  //              by more than 4 px in BOTH dimensions (grazing tolerance:
  //              borders/padding touching is not a text collision)
  // Intentional overlay text opts out with data-ov. Results go to <pre id=
  // "audit-out"> (read by the headless dump-dom runner) and to the console.
  // ?probe=sel1,sel2 — geometry diagnostics for named selectors.
  function selOf(e) {
    let s = e.id ? "#" + e.id : e.tagName.toLowerCase();
    if (!e.id && e.classList.length)
      s += "." + Array.from(e.classList).slice(0, 2).join(".");
    const sl = e.closest("section.slide");
    return sl ? sl.id + " > " + s : s;
  }

  function settledVisible(e) {
    let a = e;
    while (a && a.tagName.toLowerCase() !== "section") {
      if (a.style && a.style.visibility === "hidden") return false;
      a = a.parentElement;
    }
    return true;
  }

  function runAudit(p) {
    stage.style.transform = "none"; // measure in authoring coordinates
    slides.forEach(function (s, k) {
      const b = build(k);
      if (b.waveDur > 0) b.wave.progress(1);
      if (b.fig) b.fig.progress(1);
    });
    setTimeout(function () {
      const problems = [];
      slides.forEach(function (sl) {
        const leafs = Array.from(sl.querySelectorAll("*")).filter(function (e) {
          if (getComputedStyle(e).display === "none") return false;
          if (parseFloat(getComputedStyle(e).opacity) < 0.05) return false;
          if (!settledVisible(e)) return false; // settle-invisible (autoAlpha)
          if (e.closest("[data-ov]")) return false; // intentional overlays
          const hasText = Array.from(e.childNodes).some(function (n) {
            return n.nodeType === 3 && n.textContent.trim();
          });
          return hasText && e.textContent && e.textContent.trim();
        });
        const R = leafs.map(function (e) {
          return { e: e, b: e.getBoundingClientRect() };
        }).filter(function (r) { return r.b.width > 0 && r.b.height > 0; });
        R.forEach(function (r) {
          const b = r.b;
          if (b.left < -2 || b.top < -2 || b.right > 1922 || b.bottom > 1082)
            problems.push(`${sl.id}: OVERFLOW ${selOf(r.e)} ` +
              `[${b.left | 0},${b.top | 0} ${b.right | 0},${b.bottom | 0}]`);
        });
        for (let i = 0; i < R.length; i++) for (let j = i + 1; j < R.length; j++) {
          if (R[i].e.contains(R[j].e) || R[j].e.contains(R[i].e)) continue;
          const a = R[i].b, c = R[j].b;
          const w = Math.min(a.right, c.right) - Math.max(a.left, c.left);
          const h = Math.min(a.bottom, c.bottom) - Math.max(a.top, c.top);
          if (w > 4 && h > 4 && w * h > 120)
            problems.push(`${sl.id}: OVERLAP ${selOf(R[i].e)} x ${selOf(R[j].e)}`);
        }
      });
      const lines = ["AUDIT_RESULT " +
        JSON.stringify({ slides: slides.length, problems: problems })];
      const probes = (p.get("probe") || "")
        .split(",").map(function (s) { return s.trim(); }).filter(Boolean);
      probes.forEach(function (s) {
        const e = document.querySelector(s);
        if (!e) { lines.push(`PROBE ${s}: MISSING`); return; }
        const b = e.getBoundingClientRect();
        lines.push(`PROBE ${s}: [${b.left | 0},${b.top | 0} ` +
                   `${b.right | 0},${b.bottom | 0}]`);
      });
      const pre = document.createElement("pre");
      pre.id = "audit-out";
      pre.textContent = lines.join("\n");
      document.body.appendChild(pre);
      lines.forEach(function (l) { console.log(l); });
    }, 250);
  }

  document.addEventListener("keydown", (e) => {
    const k = e.key;
    if (k === "ArrowRight" || k === " " || k === "PageDown") show(idx + 1);
    else if (k === "ArrowLeft" || k === "PageUp") show(idx - 1);
    else if (k === "Home") show(0);
    else if (k === "End") show(N - 1);
  });

  window.addEventListener("resize", fitStage);
  window.addEventListener("beforeprint", freezeAll);
  if (window.matchMedia) {
    const mq = window.matchMedia("print");
    mq.addEventListener("change", (e) => { if (e.matches) freezeAll(); });
  }

  window.addEventListener("load", () => {
    fitStage();
    const p = new URLSearchParams(location.search);
    if (p.has("audit")) { runAudit(p); return; }
    const si = p.get("slide") ? Math.max(0, parseInt(p.get("slide"), 10) - 1) : 0;
    const t = p.has("t") ? Math.max(0, Math.min(1, parseFloat(p.get("t")))) : null;
    slides.forEach((s, k) => s.classList.toggle("active", k === si));
    if (t !== null) {
      frozen = true;
      document.documentElement.classList.add("t-pinned");
      const b = build(si);
      b.wave.pause();
      if (b.fig) b.fig.pause();
      seekSlide(si, t * b.total); // R3: same t -> same pixels
    } else if (window.gsap) {
      show(si);
    }
  });
})();
