if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/service-worker.js?v=2", { scope: "/" }).catch((error) => {
      console.error("No se pudo registrar el modo app de EDUTURNOS.", error);
    });
  });
}
