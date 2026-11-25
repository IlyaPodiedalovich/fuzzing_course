window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 4.73;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs26-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs26-b1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 1.1);
  tl.fromTo("#fs26-a1", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 0.383, ease: "none" }, 2.12);
  tl.fromTo("#fs26-b2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 2.162);
  tl.fromTo("#fs26-a2", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 0.383, ease: "none" }, 3.225);
  tl.fromTo("#fs26-b3", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 3.267);
  tl.set("#fs26-a1h", { autoAlpha: 0 }, 0);
  tl.to("#fs26-a1h", { autoAlpha: 1, duration: 0.12 }, 2.39576);
  tl.set("#fs26-a2h", { autoAlpha: 0 }, 0);
  tl.to("#fs26-a2h", { autoAlpha: 1, duration: 0.12 }, 3.50076);
  return tl;
};
