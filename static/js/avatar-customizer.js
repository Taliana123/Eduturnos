(() => {
    const trigger = document.querySelector("[data-avatar-open]");
    const dialog = document.querySelector("#avatar-customizer");
    const form = dialog?.querySelector("[data-avatar-form]");
    if (!trigger || !dialog || !form) return;

    const userId = trigger.dataset.avatarUser || "current";
    const storageKey = `eduturnos.avatar.v1:${userId}`;
    const defaultAvatar = {
        hairstyle: "short",
        hairColor: "#202b3c",
        skinColor: "#f2c7a5",
        shirtColor: "#2875c7",
    };
    const hairstyles = {
        short: {
            back: "M8 18C7 8 14 3 24 3s17 6 16 17l-2 13h-7l-1-10H18l-1 10h-7L8 18Z",
            front: "M14 17C14 8 18 5 24 5s10 4 10 12c-3-1-5-3-6-5-3 3-8 5-14 5Z",
        },
        curly: {
            back: "M8 18C6 8 13 3 17 5c3-4 7-2 9 0 6-2 12 4 12 12l-2 14h-7l-1-10H18l-1 10h-7L8 18Z",
            front: "M13 18c-1-9 4-13 7-10 2-5 7-3 8 0 5-3 9 3 7 11-3-1-5-3-7-6-3 3-9 6-15 5Z",
        },
        long: {
            back: "M8 18C7 8 14 3 24 3s17 6 16 17l-1 26h-9l-2-17H20l-2 17H9L8 18Z",
            front: "M14 17C14 8 18 5 24 5s10 4 10 12c-3-1-5-3-6-5-3 3-8 5-14 5Z",
        },
    };
    const controls = Object.fromEntries(
        [...form.querySelectorAll("select")].map((control) => [control.name, control]),
    );
    const readAvatar = () => {
        try {
            const stored = JSON.parse(window.localStorage.getItem(storageKey) || "null");
            const avatar = { ...defaultAvatar, ...(stored || {}) };
            Object.entries(controls).forEach(([name, control]) => {
                if (![...control.options].some((option) => option.value === avatar[name])) {
                    avatar[name] = defaultAvatar[name];
                }
            });
            if (!hairstyles[avatar.hairstyle]) avatar.hairstyle = defaultAvatar.hairstyle;
            return avatar;
        } catch {
            return { ...defaultAvatar };
        }
    };

    const applyAvatar = (avatar) => {
        document.querySelectorAll("[data-avatar-user]").forEach((container) => {
            if (container.dataset.avatarUser !== userId) return;
            container.dataset.hairstyle = avatar.hairstyle;
            container.style.setProperty("--avatar-hair", avatar.hairColor);
            container.style.setProperty("--avatar-skin", avatar.skinColor);
            container.style.setProperty("--avatar-shirt", avatar.shirtColor);
            container.querySelector(".user-avatar-hair-back")?.setAttribute("d", hairstyles[avatar.hairstyle].back);
            container.querySelector(".user-avatar-hair-front")?.setAttribute("d", hairstyles[avatar.hairstyle].front);
        });
        Object.entries(controls).forEach(([name, control]) => {
            if (avatar[name]) control.value = avatar[name];
        });
    };

    const saveAvatar = () => {
        const avatar = Object.fromEntries(
            Object.entries(controls).map(([name, control]) => [name, control.value]),
        );
        try {
            window.localStorage.setItem(storageKey, JSON.stringify(avatar));
            applyAvatar(avatar);
            dialog.close();
        } catch {
            applyAvatar(avatar);
        }
    };

    applyAvatar(readAvatar());
    trigger.addEventListener("click", () => {
        applyAvatar(readAvatar());
        dialog.showModal();
    });
    dialog.querySelector("[data-avatar-close]")?.addEventListener("click", () => dialog.close());
    dialog.querySelector("[data-avatar-save]")?.addEventListener("click", saveAvatar);
    dialog.querySelector("[data-avatar-reset]")?.addEventListener("click", () => {
        try {
            window.localStorage.removeItem(storageKey);
        } catch {
            // The default avatar can still be applied when storage is unavailable.
        }
        applyAvatar(defaultAvatar);
    });
    dialog.addEventListener("click", (event) => {
        if (event.target === dialog) dialog.close();
    });
})();
