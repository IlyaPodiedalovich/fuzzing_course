window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 5.41;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs14-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs14-left", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 1.1);
  tl.fromTo("#fs14-right", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 2.12);
  tl.fromTo("#fs14-note", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 3.14);
  return tl;
};
