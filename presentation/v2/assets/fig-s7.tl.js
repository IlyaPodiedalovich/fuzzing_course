window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 5.07;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs7-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs7-left", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 1.1);
  tl.fromTo("#fs7-lchips", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 1.143);
  tl.fromTo("#fs7-right", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 2.205);
  tl.fromTo("#fs7-veil", { autoAlpha: 0.16 }, { autoAlpha: 0.55, duration: 0.425, ease: "none" }, 3.225);
  tl.fromTo("#fs7-cross", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 3.31);
  tl.fromTo("#fs7-hl", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 3.437);
  return tl;
};
