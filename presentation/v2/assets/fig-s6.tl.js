window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 5.07;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs6-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs6-b1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 1.1);
  tl.fromTo("#fs6-lccn", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 2.12);
  tl.fromTo("#fs6-a1", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 0.383, ease: "none" }, 2.162);
  tl.fromTo("#fs6-b2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 2.247);
  tl.fromTo("#fs6-a2", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 0.383, ease: "none" }, 3.395);
  tl.fromTo("#fs6-b3", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 3.48);
  tl.fromTo("#fs6-lnote", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 3.607);
  tl.set("#fs6-a1h", { autoAlpha: 0 }, 0);
  tl.to("#fs6-a1h", { autoAlpha: 1, duration: 0.12 }, 2.43776);
  tl.set("#fs6-a2h", { autoAlpha: 0 }, 0);
  tl.to("#fs6-a2h", { autoAlpha: 1, duration: 0.12 }, 3.67076);
  return tl;
};
