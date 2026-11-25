window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 5.24;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs23-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs23-left", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 1.1);
  tl.fromTo("#fs23-right", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 3.14);
  tl.fromTo("#fs23-ln0", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 1.61);
  tl.fromTo("#fs23-rn0", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 3.48);
  return tl;
};
