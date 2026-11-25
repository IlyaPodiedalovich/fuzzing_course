window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 3.54;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs29-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs29-left", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 1.1);
  tl.fromTo("#fs29-right", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 2.12);
  return tl;
};
