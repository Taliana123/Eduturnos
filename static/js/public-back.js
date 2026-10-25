document.querySelectorAll(
    ".public-back-button, .institucion-back, .history-back-button, " +
    ".account-back-button, .password-account-back, .mobile-back-link, " +
    ".link-back"
).forEach((link) => {
    link.addEventListener("click", (event) => {
        if (!document.referrer || history.length < 2) return;
        try {
            if (new URL(document.referrer).origin === location.origin) {
                event.preventDefault();
                history.back();
            }
        } catch (error) {
            console.error("No se pudo validar la página anterior.", error);
        }
    });
});
