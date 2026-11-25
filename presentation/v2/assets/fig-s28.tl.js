window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 4.32;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs28-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs28-c1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 1.1);
  tl.fromTo("#fs28-c2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 1.202);
  tl.fromTo("#fs28-c3", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 1.304);
  tl.fromTo("#fs28-c4", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 1.406);
  tl.fromTo("#fs28-v1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 2.562);
  tl.fromTo("#fs28-v2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 2.647);
  tl.fromTo("#fs28-v3", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 2.732);
  tl.fromTo("#fs28-v4", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 2.817);
  return tl;
};
