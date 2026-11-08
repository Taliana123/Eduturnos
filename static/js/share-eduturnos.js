(() => {
    const qrPicker = document.querySelector("[data-qr-style]");
    const qrImage = document.querySelector(".eduturnos-share-qr-frame img");
    const dragonMark = document.querySelector("[data-qr-dragon-mark]");
    const qrFrame = document.querySelector(".eduturnos-share-qr-frame");
    const qrDescription = document.querySelector("[data-qr-description]");
    if (qrPicker && qrImage) {
        qrPicker.addEventListener("change", () => {
            const dragon = qrPicker.value === "dragon";
            qrImage.src = dragon ? qrImage.dataset.qrDragon : qrImage.dataset.qrStandard;
            qrImage.alt = dragon
                ? "Código QR azul con diseño de dragón para abrir EDUTURNOS"
                : "Código QR azul EDUTURNOS";
            dragonMark.hidden = !dragon;
            qrFrame.classList.toggle("is-dragon", dragon);
            qrDescription.textContent = dragon
                ? "Diseño Dragón: escanéalo para abrir el mismo acceso oficial de EDUTURNOS."
                : "Escanea el código para abrir EDUTURNOS e iniciar sesión.";
        });
    }

    const button = document.querySelector("[data-share-eduturnos]");
    const status = document.querySelector("[data-share-status]");
    if (!button || !status) return;

    button.addEventListener("click", async () => {
        const shareData = {
            title: "EDUTURNOS",
            text: "Conoce EDUTURNOS, la plataforma de gestión de citaciones escolares.",
            url: `${window.location.origin}/`,
        };

        try {
            if (navigator.share) {
                await navigator.share(shareData);
                status.textContent = "EDUTURNOS se compartió correctamente.";
            } else if (navigator.clipboard?.writeText) {
                await navigator.clipboard.writeText(shareData.url);
                status.textContent = "Enlace copiado. Ya puedes compartirlo.";
            } else {
                status.textContent = "No fue posible compartir desde este navegador.";
            }
        } catch (error) {
            if (error.name !== "AbortError") {
                status.textContent = "No fue posible compartir EDUTURNOS. Inténtalo de nuevo.";
                console.error("No se pudo compartir EDUTURNOS.", error);
            }
        }
    });
})();
