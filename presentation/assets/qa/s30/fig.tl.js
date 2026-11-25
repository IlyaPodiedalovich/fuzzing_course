window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 7;
  tl.set({}, {}, TOTAL);
  // b0: base rises in
  tl.fromTo("#fs30-base", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0);
  // b1: steps 1-3 nodes + arrows
  tl.fromTo("#fs30-chain1-nodes", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.6, ease: "none" }, 1.1);
  tl.fromTo("#fs30-chain1-arrows", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 1.4, ease: "none" }, 1.3);
  tl.fromTo("#fs30-chain1-tips", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, ease: "none" }, 2.55);
  // b2: steps 4-6 nodes + arrows
  tl.fromTo("#fs30-chain2-nodes", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.6, ease: "none" }, 3.5);
  tl.fromTo("#fs30-chain2-arrows", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 1.5, ease: "none" }, 3.6);
  tl.fromTo("#fs30-chain2-tips", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, ease: "none" }, 5.0);
  return tl;
};
