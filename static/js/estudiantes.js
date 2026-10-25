document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#student-form");
    if (!form) return;

    const grade = form.querySelector('[name="grado"]');
    const group = form.querySelector('[name="grupo"]');
    if (grade && group) {
        const refreshGroups = () => {
            for (const option of group.options) {
                if (!option.value) continue;
                const visible = option.dataset.grade === grade.value &&
                    ["1", "2", "3", "4", "5", "6"].includes(option.dataset.groupNumber);
                option.hidden = !visible;
                option.disabled = !visible;
            }
            if (group.selectedOptions.length && group.selectedOptions[0].disabled) group.value = "";
            group.disabled = !grade.value;
        };

        grade.addEventListener("change", refreshGroups);
        refreshGroups();
    }

    form.querySelectorAll("[data-digits-only]").forEach((field) => {
        field.addEventListener("input", () => {
            field.value = field.value.replace(/[^0-9]/g, "");
        });
    });

    form.querySelectorAll("[data-letters-only]").forEach((field) => {
        field.addEventListener("input", () => {
            field.value = field.value.replace(/[^A-Za-zÁÉÍÓÚÑÜáéíóúñü ]/g, "");
        });
    });

    form.addEventListener("submit", () => {
        const button = form.querySelector('button[type="submit"]');
        if (!button) return;
        button.disabled = true;
        button.textContent = "Guardando…";
        form.setAttribute("aria-busy", "true");
    });
});
