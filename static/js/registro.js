document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".portal-registro-form");
    if (!form) return;

    let values;
    try {
        values = JSON.parse(form.dataset.formValues || "{}");
    } catch (error) {
        console.error("No se pudieron restaurar los datos del formulario de registro.", error);
        return;
    }

    for (const field of form.elements) {
        if (
            !field.name ||
            field.type === "password" ||
            !Object.prototype.hasOwnProperty.call(values, field.name)
        ) {
            continue;
        }
        field.value = values[field.name];
    }

    form.querySelectorAll('input[type="email"][pattern]').forEach((field) => {
        field.addEventListener("blur", () => {
            if (!field.value || !field.checkValidity()) {
                field.reportValidity();
            }
        });
    });

    form.querySelectorAll("select[data-grupo-de]").forEach((groupSelect) => {
        const gradeSelect = form.querySelector(
            `select[name="${groupSelect.dataset.grupoDe}"]`
        );
        if (!gradeSelect) return;

        const placeholder = groupSelect.querySelector('option[value=""]');
        const groupOptions = Array.from(groupSelect.options)
            .filter((option) => option.dataset.idGrado)
            .map((option) => option.cloneNode(true));
        let selectedGroup = groupSelect.value;

        const updateGroups = () => {
            const gradeId = gradeSelect.value;
            const matchingGroups = groupOptions.filter(
                (option) => option.dataset.idGrado === gradeId
            );

            groupSelect.replaceChildren(
                placeholder.cloneNode(true),
                ...matchingGroups.map((option) => option.cloneNode(true))
            );
            groupSelect.disabled = !gradeId;
            groupSelect.options[0].textContent = gradeId
                ? "Selecciona un grupo"
                : "Primero selecciona un grado";

            if (matchingGroups.some((option) => option.value === selectedGroup)) {
                groupSelect.value = selectedGroup;
            } else {
                selectedGroup = "";
                groupSelect.value = "";
            }
        };

        gradeSelect.addEventListener("change", () => {
            selectedGroup = "";
            updateGroups();
        });
        groupSelect.addEventListener("change", () => {
            selectedGroup = groupSelect.value;
        });
        groupSelect.addEventListener("blur", () => {
            if (gradeSelect.value && !groupSelect.value) {
                groupSelect.reportValidity();
            }
        });

        updateGroups();
    });

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
        button.textContent = "Enviando…";
        form.setAttribute("aria-busy", "true");
    });
});
