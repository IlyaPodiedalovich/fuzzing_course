window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 6;
  tl.set({}, {}, TOTAL);
  // b0: base rises in
  tl.fromTo("#fs1-base", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0);
  // b1: chain nodes light, chain arrows draw
  tl.fromTo("#fs1-chain-nodes", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.8);
  tl.fromTo("#fs1-chain-arrows", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 1.2, ease: "none" }, 0.9);
  tl.fromTo("#fs1-chain-tips", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, ease: "none" }, 2.0);
  // b2: diamond + branches
  tl.fromTo("#fs1-dia-accent", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 2.95);
  tl.fromTo("#fs1-diamond-branches", { strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 1.3, ease: "none" }, 3.0);
  tl.fromTo("#fs1-diamond-tips", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, ease: "none" }, 4.1);
  return tl;
};
