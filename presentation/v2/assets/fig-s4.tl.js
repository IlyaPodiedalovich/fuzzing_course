window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 4.82;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs4-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs4-b1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 1.1);
  tl.fromTo("#fs4-b2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 2.12);
  tl.fromTo("#fs4-a1", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 0.383, ease: "none" }, 2.162);
  tl.fromTo("#fs4-b3", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 3.141);
  tl.fromTo("#fs4-a2", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 0.383, ease: "none" }, 3.183);
  tl.fromTo("#fs4-tbl", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.383, ease: "none" }, 3.311);
  tl.set("#fs4-a1h", { autoAlpha: 0 }, 0);
  tl.to("#fs4-a1h", { autoAlpha: 1, duration: 0.12 }, 2.43776);
  tl.set("#fs4-a2h", { autoAlpha: 0 }, 0);
  tl.to("#fs4-a2h", { autoAlpha: 1, duration: 0.12 }, 3.45876);
  return tl;
};
