(() => {
    const mascot = document.querySelector("[data-edubot-mascot]");
    if (!mascot || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    let frame = 0;
    let pointerX = window.innerWidth / 2;
    let pointerY = window.innerHeight / 2;

    const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

    const updatePosition = () => {
        frame = 0;
        const bounds = mascot.getBoundingClientRect();
        const centerX = bounds.left + bounds.width / 2;
        const centerY = bounds.top + bounds.height / 2;
        const x = clamp((pointerX - centerX) / Math.max(window.innerWidth / 2, 1) * 10, -10, 10);
        const y = clamp((pointerY - centerY) / Math.max(window.innerHeight / 2, 1) * 8, -8, 8);

        mascot.style.setProperty("--edubot-x", `${x.toFixed(1)}px`);
        mascot.style.setProperty("--edubot-y", `${y.toFixed(1)}px`);
        mascot.style.setProperty("--edubot-tilt", `${(x * 0.3).toFixed(1)}deg`);
    };

    const followPointer = (event) => {
        pointerX = event.clientX;
        pointerY = event.clientY;
        if (!frame) frame = window.requestAnimationFrame(updatePosition);
    };

    window.addEventListener("pointermove", followPointer, { passive: true });
    window.addEventListener("pointerdown", (event) => {
        const bounds = mascot.getBoundingClientRect();
        if (
            event.clientX < bounds.left || event.clientX > bounds.right ||
            event.clientY < bounds.top || event.clientY > bounds.bottom
        ) return;

        mascot.classList.remove("is-tapped");
        void mascot.offsetWidth;
        mascot.classList.add("is-tapped");
    }, { passive: true });

    mascot.addEventListener("animationend", (event) => {
        if (event.animationName === "edubot-mascot-bounce") {
            mascot.classList.remove("is-tapped");
        }
    });
})();
