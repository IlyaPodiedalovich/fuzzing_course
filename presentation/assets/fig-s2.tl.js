window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 5;
  tl.set({}, {}, TOTAL);
  // b0: base rises in
  tl.fromTo("#fs2-base", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0);
  // b1: bottom box accent + left annotation
  tl.fromTo("#fs2-bottom", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 1.0);
  // b2: middle box accent + arrows draw + tips + right annotation
  tl.fromTo("#fs2-middle-rect", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 2.3);
  tl.fromTo("#fs2-arrows", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 1.5, ease: "none" }, 2.3);
  tl.fromTo("#fs2-middle-tips", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, ease: "none" }, 3.7);
  tl.fromTo("#fs2-right-note", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4, ease: "none" }, 2.6);
  return tl;
};
