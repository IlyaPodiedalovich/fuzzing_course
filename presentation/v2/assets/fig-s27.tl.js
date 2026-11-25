window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 5.16;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs27-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs27-b1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 1.1);
  tl.fromTo("#fs27-a1", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 0.383, ease: "none" }, 2.12);
  tl.fromTo("#fs27-b2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 2.162);
  tl.fromTo("#fs27-c1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 2.29);
  tl.fromTo("#fs27-c2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 2.375);
  tl.fromTo("#fs27-c3", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 2.46);
  tl.fromTo("#fs27-a2", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 0.383, ease: "none" }, 3.65);
  tl.fromTo("#fs27-b3", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 3.692);
  tl.set("#fs27-a1h", { autoAlpha: 0 }, 0);
  tl.to("#fs27-a1h", { autoAlpha: 1, duration: 0.12 }, 2.39576);
  tl.set("#fs27-a2h", { autoAlpha: 0 }, 0);
  tl.to("#fs27-a2h", { autoAlpha: 1, duration: 0.12 }, 3.92576);
  return tl;
};
