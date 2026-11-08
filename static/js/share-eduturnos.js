(() => {
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
