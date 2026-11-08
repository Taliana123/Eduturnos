(() => {
    const qrPicker = document.querySelector("[data-qr-style]");
    const qrImage = document.querySelector(".eduturnos-share-qr-frame img");
    const qrFrame = document.querySelector(".eduturnos-share-qr-frame");
    const qrDescription = document.querySelector("[data-qr-description]");
    if (qrPicker && qrImage) {
        qrPicker.addEventListener("change", () => {
            const navy = qrPicker.value === "navy";
            qrImage.src = navy ? qrImage.dataset.qrNavy : qrImage.dataset.qrBlue;
            qrImage.alt = navy
                ? "Código QR azul institucional para abrir el sitio oficial de EDUTURNOS"
                : "Código QR azul de EDUTURNOS para abrir el sitio oficial";
            qrFrame.classList.toggle("is-navy", navy);
            qrDescription.textContent = "Escanea el código para abrir EDUTURNOS e iniciar sesión.";
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
