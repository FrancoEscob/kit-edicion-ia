/* Todos los tiempos son segundos del montaje. El render puede saltar de cuadro. */
window.PovCel = (() => {
  function camera(tl, planes, poses, pan = 1) {
    const depths = [0.48, 1, 1.6];
    let previous = 0;
    poses.forEach(({ at, x = 0, y = 0, zoom = 1, roll = 0, ease = "sine.inOut" }, index) => {
      planes.forEach((plane, depth) => {
        const factor = depths[depth];
        const pose = {
          x: x * factor * pan, y: y * factor * pan,
          rotation: roll * (0.65 + factor * 0.35) * pan,
          scale: 1.15 + (zoom - 1) * factor * pan
        };
        if (index === 0) tl.set(plane, pose, at);
        else tl.to(plane, { ...pose, duration: at - previous, ease }, previous);
      });
      previous = at;
    });
  }

  function reach(tl, hand, at, { x, y, rotation = 0, travel = 0.43, hold = 0.53, returnTime = 0.5 }) {
    tl.to(hand, { x, y, rotation, duration: travel, ease: "power2.out" }, at);
    tl.to(hand, { x: 0, y: 0, rotation: 0, duration: returnTime, ease: "sine.inOut" }, at + travel + hold);
  }

  function whip(tl, cover, at, { frames = 5, fps = 30, color = "#153749", flash = false } = {}) {
    const half = frames / fps / 2;
    tl.set(cover, { backgroundColor: color }, at - half);
    if (flash) {
      tl.fromTo(cover, { opacity: 0 }, { opacity: 0.82, duration: half, ease: "none" }, at - half);
      tl.to(cover, { opacity: 0, duration: half, ease: "none" }, at);
    } else {
      tl.fromTo(cover, { xPercent: -110, opacity: 1 }, { xPercent: 0, duration: half, ease: "power2.in" }, at - half);
      tl.to(cover, { xPercent: 110, duration: half, ease: "power2.out" }, at);
      tl.set(cover, { opacity: 0 }, at + half);
    }
  }

  function endCard(tl, card, at) {
    const rows = card.querySelectorAll(".choice");
    const frame = 1 / 30;
    tl.fromTo(card, { opacity: 0 }, { opacity: 1, duration: 6 * frame, ease: "power1.out" }, at);
    tl.fromTo(rows, { scale: 0.53, opacity: 0 }, {
      scale: 1, opacity: 1, duration: 3 * frame, stagger: 2 * frame, ease: "power2.out"
    }, at + frame);
  }

  return { camera, reach, whip, endCard };
})();
