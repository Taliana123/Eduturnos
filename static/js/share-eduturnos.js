(() => {
    const qrPicker = document.querySelector("[data-qr-style]");
    const qrImage = document.querySelector(".eduturnos-qr-code-image");
    const qrFrame = document.querySelector(".eduturnos-share-qr-frame");
    if (qrPicker && qrImage) {
        qrPicker.addEventListener("change", () => {
            const dragon = qrPicker.value === "dragon";
            qrImage.src = dragon ? qrImage.dataset.qrDragon : qrImage.dataset.qrInstitutional;
            qrImage.alt = dragon
                ? "Código QR para abrir EDUTURNOS, integrado al diseño del dragón"
                : "Código QR azul para abrir EDUTURNOS";
            qrFrame.classList.toggle("is-dragon", dragon);
            qrFrame.classList.toggle("is-institutional", !dragon);
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
