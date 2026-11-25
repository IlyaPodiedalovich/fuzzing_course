window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 6.11;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs19-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs19-track", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.05);
  tl.fromTo("#fs19-bar", { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.765, ease: "none" }, 1.242);
  tl.fromTo("#fs19-badge", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.383, ease: "none" }, 3.07);
  tl.fromTo("#fs19-lead", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 0.297, ease: "none" }, 3.155);
  tl.fromTo("#fs19-pct", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.383, ease: "none" }, 3.197);
  tl.fromTo("#fs19-m1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.383, ease: "none" }, 4.346);
  tl.fromTo("#fs19-m2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.383, ease: "none" }, 4.431);
  tl.fromTo("#fs19-exec", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.383, ease: "none" }, 4.559);
  tl.set("#fs19-leadh", { autoAlpha: 0 }, 0);
  tl.to("#fs19-leadh", { autoAlpha: 1, duration: 0.12 }, 3.3688399999999996);
  return tl;
};
