(() => {
    const triggers = [...document.querySelectorAll("[data-avatar-open]")];
    const dialog = document.querySelector("#avatar-customizer");
    const form = dialog?.querySelector("[data-avatar-form]");
    if (!triggers.length || !dialog || !form) return;

    const userId = triggers[0].dataset.avatarUser;
    const storageKey = `eduturnos.avatar.v1:${userId}`;
    const fields = [...dialog.querySelectorAll("[data-avatar-choice]")];
    const choices = new Map();
    fields.forEach((choice) => {
        const values = choices.get(choice.dataset.field) || new Set();
        values.add(choice.dataset.value);
        choices.set(choice.dataset.field, values);
    });
    const initialAvatar = JSON.parse(triggers[0].dataset.avatarConfig);
    const status = dialog.querySelector("[data-avatar-status]");
    const saveButton = dialog.querySelector("[data-avatar-save]");
    const csrfToken = form.querySelector('input[name="csrf_token"]').value;
    let currentAvatar = { ...initialAvatar };

    const isValidAvatar = (avatar) => avatar && [...choices].every(
        ([field, values]) => typeof avatar[field] === "string" && values.has(avatar[field]),
    );

    const applyAvatar = (avatar) => {
        currentAvatar = { ...avatar };
        document.querySelectorAll("[data-avatar-user]").forEach((container) => {
            if (container.dataset.avatarUser !== userId) return;
            const drawing = container.querySelector(".user-avatar-drawing");
            if (!drawing) return;

            drawing.dataset.character = avatar.character;
            drawing.dataset.ageStyle = avatar.ageStyle;
            drawing.dataset.hairstyle = avatar.hairstyle;
            drawing.dataset.outfit = avatar.outfit;
            drawing.dataset.accessory = avatar.accessory;
            drawing.style.setProperty("--avatar-hair", avatar.hairColor);
            drawing.style.setProperty("--avatar-skin", avatar.skinColor);
            drawing.style.setProperty("--avatar-eyes", avatar.eyeColor);
            drawing.style.setProperty("--avatar-shirt", avatar.shirtColor);
        });
        fields.forEach((choice) => {
            choice.setAttribute(
                "aria-pressed",
                String(avatar[choice.dataset.field] === choice.dataset.value),
            );
        });
    };

    const legacyAvatar = () => {
        try {
            const oldAvatar = JSON.parse(window.localStorage.getItem(storageKey) || "null");
            if (!oldAvatar) return null;
            const hairColors = {
                "#202b3c": "#282331",
                "#71452e": "#69432f",
                "#d6a542": "#c99537",
                "#a94755": "#a84d35",
            };
            const skinColors = {
                "#f2c7a5": "#efc19a",
                "#a96f51": "#89583f",
            };
            const migrated = {
                character: "neutral",
                ageStyle: "teen",
                hairstyle: oldAvatar.hairstyle || (oldAvatar.portrait === "glasses" ? "curly" : "short"),
                hairColor: hairColors[oldAvatar.hairColor] || oldAvatar.hairColor,
                skinColor: skinColors[oldAvatar.skinColor] || oldAvatar.skinColor,
                eyeColor: "#493124",
                outfit: oldAvatar.portrait === "cap" ? "hoodie" : "shirt",
                shirtColor: oldAvatar.shirtColor,
                accessory: oldAvatar.portrait === "cap" ? "cap" : oldAvatar.portrait === "glasses" ? "glasses" : "none",
            };
            return isValidAvatar(migrated) ? migrated : null;
        } catch (error) {
            console.error("No se pudo recuperar la personalización anterior del avatar.", error);
            return null;
        }
    };

    const saveToServer = async (avatar) => {
        const response = await fetch(form.dataset.avatarSaveUrl, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify(avatar),
        });
        const result = await response.json();
        if (!response.ok || !result.ok) {
            throw new Error(result.error || "No fue posible guardar el personaje.");
        }
        return result.avatar;
    };

    const clearLegacyStorage = () => {
        try {
            window.localStorage.removeItem(storageKey);
        } catch (error) {
            console.warn("No se pudo limpiar la copia local antigua del avatar.", error);
        }
    };

    applyAvatar(initialAvatar);
    triggers.forEach((trigger) => {
        trigger.addEventListener("click", () => {
            applyAvatar(currentAvatar);
            status.textContent = "";
            dialog.showModal();
        });
    });

    fields.forEach((choice) => {
        choice.addEventListener("click", () => {
            applyAvatar({ ...currentAvatar, [choice.dataset.field]: choice.dataset.value });
        });
    });

    dialog.querySelector("[data-avatar-close]")?.addEventListener("click", () => dialog.close());
    dialog.querySelector("[data-avatar-reset]")?.addEventListener("click", () => {
        applyAvatar(initialAvatar);
        status.textContent = "Vista previa restablecida. Guarda para confirmar el cambio.";
    });
    saveButton?.addEventListener("click", async () => {
        saveButton.disabled = true;
        status.textContent = "Guardando tu personaje…";
        try {
            const savedAvatar = await saveToServer(currentAvatar);
            applyAvatar(savedAvatar);
            triggers.forEach((trigger) => {
                trigger.dataset.avatarConfig = JSON.stringify(savedAvatar);
            });
            status.textContent = "Tu personaje quedó guardado en tu cuenta.";
            clearLegacyStorage();
            dialog.close();
        } catch (error) {
            status.textContent = error.message || "No fue posible guardar el personaje. Inténtalo de nuevo.";
            console.error("No se pudo guardar el avatar de EDUTURNOS.", error);
        } finally {
            saveButton.disabled = false;
        }
    });
    dialog.addEventListener("click", (event) => {
        if (event.target === dialog) dialog.close();
    });

    const migratedAvatar = legacyAvatar();
    if (migratedAvatar) {
        applyAvatar(migratedAvatar);
        saveToServer(migratedAvatar)
            .then((savedAvatar) => {
                applyAvatar(savedAvatar);
                triggers.forEach((trigger) => {
                    trigger.dataset.avatarConfig = JSON.stringify(savedAvatar);
                });
                clearLegacyStorage();
            })
            .catch((error) => {
                console.error("No se pudo migrar el avatar guardado en este dispositivo.", error);
            });
    }
})();
