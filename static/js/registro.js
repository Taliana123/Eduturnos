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
