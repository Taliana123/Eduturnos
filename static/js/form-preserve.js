document.addEventListener("DOMContentLoaded", () => {
    const storageKey = "eduturnos:form-recovery";
    const currentPath = `${window.location.pathname}${window.location.search}`;
    const forms = Array.from(document.forms);
    const errorNotice = document.querySelector(
        "#contenido .alerta.error, #contenido .alerta.danger, #contenido .alert.alert-error, #contenido .alert.alert-danger, #contenido [data-form-error]"
    );

    let storage;
    try {
        storage = window.sessionStorage;
    } catch (error) {
        console.error("El navegador no permite guardar temporalmente los datos del formulario.", error);
        return;
    }

    try {
        const stored = JSON.parse(storage.getItem(storageKey) || "null");
        if (stored) {
            const form = forms[stored.formIndex];
            if (
                stored.path === currentPath &&
                Date.now() - stored.timestamp < 15 * 60 * 1000 &&
                errorNotice &&
                form
            ) {
                for (const saved of stored.fields) {
                    const field = form.elements.item(saved.index);
                    if (!field || field.name !== saved.name || field.type === "password") continue;
                    if (field.type === "checkbox" || field.type === "radio") {
                        field.checked = saved.checked;
                    } else if (field.tagName === "SELECT" && field.multiple) {
                        for (const option of field.options) {
                            option.selected = saved.selected.includes(option.value);
                        }
                    } else {
                        field.value = saved.value;
                    }
                }
            }
            storage.removeItem(storageKey);
        }
    } catch (error) {
        console.error("No se pudieron restaurar los datos del formulario.", error);
        try {
            storage.removeItem(storageKey);
        } catch (cleanupError) {
            console.error("No se pudieron borrar los datos temporales del formulario.", cleanupError);
        }
    }

    forms.forEach((form, formIndex) => {
        if (form.method.toUpperCase() !== "POST") return;
        form.addEventListener("submit", () => {
            const fields = Array.from(form.elements)
                .map((field, index) => ({ field, index }))
                .filter(({ field }) =>
                    field.name &&
                    field.name !== "csrf_token" &&
                    field.type !== "password" &&
                    field.type !== "file" &&
                    field.type !== "submit" &&
                    field.type !== "button" &&
                    field.type !== "reset" &&
                    field.type !== "image" &&
                    field.type !== "hidden"
                )
                .map(({ field, index }) => ({
                    index,
                    name: field.name,
                    type: field.type,
                    value: field.value,
                    checked: field.checked,
                    selected: field.tagName === "SELECT" && field.multiple
                        ? Array.from(field.selectedOptions, (option) => option.value)
                        : [],
                }));

            try {
                storage.setItem(storageKey, JSON.stringify({
                    path: currentPath,
                    formIndex,
                    timestamp: Date.now(),
                    fields,
                }));
            } catch (error) {
                console.error("No se pudieron guardar temporalmente los datos del formulario.", error);
            }
        });
    });
});
