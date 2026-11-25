window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 6.01;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs12-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs12-p1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 1.1);
  tl.fromTo("#fs12-c1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.383, ease: "none" }, 1.312);
  tl.fromTo("#fs12-p2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 2.461);
  tl.fromTo("#fs12-c2a", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.383, ease: "none" }, 2.588);
  tl.fromTo("#fs12-a2", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 0.297, ease: "none" }, 2.673);
  tl.fromTo("#fs12-c2b", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.383, ease: "none" }, 2.758);
  tl.fromTo("#fs12-p3", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.425, ease: "none" }, 3.992);
  tl.fromTo("#fs12-s0", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.383, ease: "none" }, 4.162);
  tl.fromTo("#fs12-s1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.383, ease: "none" }, 4.247);
  tl.fromTo("#fs12-s2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.383, ease: "none" }, 4.332);
  tl.set("#fs12-a2h", { autoAlpha: 0 }, 0);
  tl.to("#fs12-a2h", { autoAlpha: 1, duration: 0.12 }, 2.88684);
  return tl;
};
