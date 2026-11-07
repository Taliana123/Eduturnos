(() => {
    const directions = [
        "up-left", "up", "up-right",
        "left", "center", "right",
        "down-left", "down", "down-right",
    ];
    const reactions = [
        "blink", "heart", "sparkle",
        "surprised", "wink", "bashful",
        "sleepy", "dizzy", "delighted",
    ];
    const clockwise = [
        "right", "down-right", "down", "down-left",
        "left", "up-left", "up", "up-right",
    ];
    const sectorSize = (Math.PI * 2) / clockwise.length;
    const hysteresis = 0.12;
    const payoffReactions = ["heart", "sparkle", "delighted"];

    document.querySelectorAll("[data-page-mascot]").forEach((mascot) => {
        const frame = mascot.querySelector("[data-mascot-frame]");
        const directionsLayer = mascot.querySelector("[data-mascot-directions]");
        const reactionsLayer = mascot.querySelector("[data-mascot-reactions]");
        if (!frame || !directionsLayer || !reactionsLayer) return;

        let activeSector = -1;
        let pointer = null;
        let boopCount = 0;
        let lastBoopAt = 0;
        let timers = [];
        let bounceTimer = 0;
        let dragState = null;
        let dragged = false;
        let suppressClickTimer = 0;

        const setCell = (layer, names, name) => {
            const index = names.indexOf(name);
            layer.style.backgroundPosition = `${(index % 3) * 50}% ${Math.floor(index / 3) * 50}%`;
        };

        const showReaction = (name) => {
            if (name) {
                setCell(reactionsLayer, reactions, name);
                directionsLayer.classList.remove("is-visible");
                reactionsLayer.classList.add("is-visible");
                return;
            }
            reactionsLayer.classList.remove("is-visible");
            directionsLayer.classList.add("is-visible");
        };

        const aim = () => {
            if (!pointer) return;
            const bounds = mascot.getBoundingClientRect();
            const dx = pointer.x - (bounds.left + bounds.width / 2);
            const dy = pointer.y - (bounds.top + bounds.height / 2);
            if (Math.hypot(dx, dy) < 70) {
                activeSector = -1;
                setCell(directionsLayer, directions, "center");
                return;
            }

            const angle = Math.atan2(dy, dx);
            const heldAngle = activeSector * sectorSize;
            const difference = Math.atan2(Math.sin(angle - heldAngle), Math.cos(angle - heldAngle));
            if (activeSector !== -1 && Math.abs(difference) < sectorSize / 2 + hysteresis) return;

            activeSector = (Math.round(angle / sectorSize) + clockwise.length) % clockwise.length;
            setCell(directionsLayer, directions, clockwise[activeSector]);
        };

        const updateGaze = (event) => {
            pointer = { x: event.clientX, y: event.clientY };
            const bounds = mascot.getBoundingClientRect();
            if (
                pointer.x >= bounds.left && pointer.x <= bounds.right
                && pointer.y >= bounds.top && pointer.y <= bounds.bottom
            ) return;
            aim();
        };
        window.addEventListener("pointermove", updateGaze, { passive: true });
        window.addEventListener("pointerdown", updateGaze, { passive: true });
        window.addEventListener("scroll", aim, { passive: true });

        if (mascot.classList.contains("page-mascot--floating")) {
            let startLeft = 0;
            let startTop = 0;
            const positionKey = "eduturnos.pageMascot.position";

            const clampPosition = (left, top) => {
                const bounds = mascot.getBoundingClientRect();
                return {
                    left: Math.min(Math.max(8, left), Math.max(8, window.innerWidth - bounds.width - 8)),
                    top: Math.min(Math.max(8, top), Math.max(8, window.innerHeight - bounds.height - 8)),
                };
            };

            const placeAt = (left, top) => {
                const position = clampPosition(left, top);
                mascot.style.left = `${position.left}px`;
                mascot.style.top = `${position.top}px`;
                mascot.style.right = "auto";
                mascot.style.bottom = "auto";
            };

            const savePosition = () => {
                try {
                    const bounds = mascot.getBoundingClientRect();
                    window.localStorage.setItem(positionKey, JSON.stringify({
                        left: bounds.left,
                        top: bounds.top,
                    }));
                } catch (error) {
                    console.warn("No se pudo guardar la posición del agente de EDUTURNOS.", error);
                }
            };

            const hasSavedPosition = () => {
                try {
                    return Boolean(window.localStorage.getItem(positionKey));
                } catch (error) {
                    console.warn("No se pudo consultar la posición guardada del agente de EDUTURNOS.", error);
                    return false;
                }
            };

            try {
                const saved = JSON.parse(window.localStorage.getItem(positionKey) || "null");
                if (
                    saved
                    && Number.isFinite(saved.left)
                    && Number.isFinite(saved.top)
                ) {
                    placeAt(saved.left, saved.top);
                }
            } catch (error) {
                console.warn("No se pudo restaurar la posición del agente de EDUTURNOS.", error);
            }

            mascot.addEventListener("pointerdown", (event) => {
                if (!event.isPrimary || (event.pointerType === "mouse" && event.button !== 0)) return;
                const bounds = mascot.getBoundingClientRect();
                startLeft = bounds.left;
                startTop = bounds.top;
                dragState = {
                    pointerId: event.pointerId,
                    startX: event.clientX,
                    startY: event.clientY,
                    moved: false,
                };
                mascot.setPointerCapture(event.pointerId);
                mascot.classList.add("is-dragging");
                event.preventDefault();
            });

            mascot.addEventListener("pointermove", (event) => {
                if (!dragState || event.pointerId !== dragState.pointerId) return;
                const deltaX = event.clientX - dragState.startX;
                const deltaY = event.clientY - dragState.startY;
                if (!dragState.moved && Math.hypot(deltaX, deltaY) < 5) return;
                dragState.moved = true;
                placeAt(startLeft + deltaX, startTop + deltaY);
            });

            const finishDrag = (event) => {
                if (!dragState || event.pointerId !== dragState.pointerId) return;
                dragged = dragState.moved;
                dragState = null;
                mascot.classList.remove("is-dragging");
                if (dragged) {
                    savePosition();
                    window.clearTimeout(suppressClickTimer);
                    suppressClickTimer = window.setTimeout(() => {
                        dragged = false;
                    }, 250);
                }
            };

            mascot.addEventListener("pointerup", finishDrag);
            mascot.addEventListener("pointercancel", finishDrag);
            window.addEventListener("resize", () => {
                if (hasSavedPosition()) {
                    const bounds = mascot.getBoundingClientRect();
                    placeAt(bounds.left, bounds.top);
                    savePosition();
                }
            });

            mascot.addEventListener("keydown", (event) => {
                const movement = {
                    ArrowUp: [0, -20],
                    ArrowDown: [0, 20],
                    ArrowLeft: [-20, 0],
                    ArrowRight: [20, 0],
                }[event.key];
                if (!movement) return;
                const bounds = mascot.getBoundingClientRect();
                placeAt(bounds.left + movement[0], bounds.top + movement[1]);
                savePosition();
                event.preventDefault();
            });
        }

        mascot.addEventListener("click", (event) => {
            if (dragged) {
                dragged = false;
                event.preventDefault();
                event.stopImmediatePropagation();
                return;
            }
            timers.forEach(window.clearTimeout);
            timers = [];

            const now = Date.now();
            boopCount = now - lastBoopAt < 1600 ? boopCount + 1 : 1;
            lastBoopAt = now;
            if (boopCount >= 4) {
                boopCount = 0;
                showReaction("dizzy");
                timers.push(window.setTimeout(() => showReaction(null), 1100));
            } else {
                showReaction("blink");
                timers.push(window.setTimeout(() => {
                    showReaction(payoffReactions[(boopCount - 1) % payoffReactions.length]);
                }, 120));
                timers.push(window.setTimeout(() => showReaction(null), 560));
            }

            if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
                window.clearTimeout(bounceTimer);
                frame.classList.remove("is-booping");
                void frame.offsetWidth;
                frame.classList.add("is-booping");
                bounceTimer = window.setTimeout(() => frame.classList.remove("is-booping"), 420);
            }
        });
    });
})();
