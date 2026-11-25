window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 4.7;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs21-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs21-c1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 1.1);
  tl.fromTo("#fs21-c2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 1.202);
  tl.fromTo("#fs21-c3", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 1.304);
  tl.fromTo("#fs21-c4", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 1.406);
  tl.fromTo("#fs21-c5", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 1.508);
  tl.fromTo("#fs21-v1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 2.766);
  tl.fromTo("#fs21-v2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 2.851);
  tl.fromTo("#fs21-v3", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 2.936);
  tl.fromTo("#fs21-v4", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 3.021);
  tl.fromTo("#fs21-v5", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 3.106);
  return tl;
};
