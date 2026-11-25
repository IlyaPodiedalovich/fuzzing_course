window.FigTl = (gsap) => {
  const tl = gsap.timeline({ paused: true });
  const TOTAL = 5.42;
  tl.set({}, {}, TOTAL);
  tl.fromTo("#fs24-all", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.0);
  tl.fromTo("#fs24-ax", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.5, ease: "none" }, 0.05);
  tl.fromTo("#fs24-l0", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.4, ease: "none" }, 0.15);
  tl.fromTo("#fs24-l1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.4, ease: "none" }, 0.15);
  tl.fromTo("#fs24-l2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.4, ease: "none" }, 0.15);
  tl.fromTo("#fs24-b1", { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.595, ease: "none" }, 1.242);
  tl.fromTo("#fs24-v1", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 1.71);
  tl.fromTo("#fs24-b2", { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.595, ease: "none" }, 3.07);
  tl.fromTo("#fs24-b3", { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.595, ease: "none" }, 3.197);
  tl.fromTo("#fs24-v2", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 3.537);
  tl.fromTo("#fs24-v3", { autoAlpha: 0.16 }, { autoAlpha: 1, duration: 0.34, ease: "none" }, 3.622);
  return tl;
};
