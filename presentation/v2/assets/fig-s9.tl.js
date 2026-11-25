window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 5.58;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs9-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs9-c1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 1.1);
  tl.fromTo("#fs9-c2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 2.12);
  tl.fromTo("#fs9-c3", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 3.14);
  tl.fromTo("#fs9-c4", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 4.16);
  return tl;
};
