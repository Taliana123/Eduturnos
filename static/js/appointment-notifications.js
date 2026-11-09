(() => {
    "use strict";

    const nativeNotifications = window.EDUTURNOSNativeNotifications;
    if (!nativeNotifications) return;

    const settings = document.querySelector("[data-appointment-notification-settings]");
    const enableButton = document.querySelector("[data-appointment-notifications-enable]");
    const status = document.querySelector("[data-appointment-notifications-status]");
    let requestPending = false;
    if (settings) settings.hidden = false;

    const showStatus = (message) => {
        if (!status) return;
        status.textContent = message;
        status.hidden = false;
    };

    const synchronizeAppointments = async () => {
        const response = await fetch("/notificaciones/api/citas-futuras", {
            credentials: "same-origin",
            cache: "no-store",
            headers: { Accept: "application/json" },
        });
        if (response.status === 401) {
            nativeNotifications.cancelAll();
            return;
        }
        if (!response.ok) {
            throw new Error(`No se pudieron consultar las citas (${response.status}).`);
        }
        const result = await response.json();
        if (!result || !Array.isArray(result.appointments)) {
            throw new Error("La respuesta de citas no tiene un formato válido.");
        }
        nativeNotifications.schedule(JSON.stringify(result.appointments));
    };

    window.addEventListener("eduturnos-native-notifications-permission", (event) => {
        requestPending = false;
        if (enableButton) enableButton.disabled = false;
        if (event.detail?.granted) {
            if (enableButton) enableButton.hidden = true;
            synchronizeAppointments().catch((error) => {
                console.error("No se pudieron actualizar los recordatorios de citas.", error);
                showStatus("No se pudieron actualizar los recordatorios. Inténtalo de nuevo más tarde.");
            });
        } else {
            showStatus("No se concedió el permiso. Puedes habilitar las notificaciones de EDUTURNOS desde Ajustes de Android.");
        }
    });

    window.addEventListener("eduturnos-native-notifications-scheduled", (event) => {
        if (event.detail?.ok && status) {
            showStatus("Los recordatorios de citas de este dispositivo están actualizados.");
        }
    });

    window.addEventListener("eduturnos-native-notifications-error", () => {
        showStatus("No se pudieron programar los recordatorios de citas. Inténtalo de nuevo más tarde.");
    });

    if (enableButton) {
        enableButton.hidden = false;
        enableButton.addEventListener("click", () => {
            if (requestPending) return;
            requestPending = true;
            enableButton.disabled = true;
            nativeNotifications.requestPermission();
        });
    }

    if (nativeNotifications.hasPermission()) {
        if (enableButton) enableButton.hidden = true;
        synchronizeAppointments().catch((error) => {
            console.error("No se pudieron actualizar los recordatorios de citas.", error);
            showStatus("No se pudieron actualizar los recordatorios. Inténtalo de nuevo más tarde.");
        });
    }
})();
