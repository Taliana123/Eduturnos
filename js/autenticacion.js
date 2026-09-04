document.addEventListener("DOMContentLoaded", function () {

    const formulario = document.getElementById("formLogin");

    if (!formulario) {
        return;
    }

    formulario.addEventListener("submit", function (evento) {

        evento.preventDefault();

        const correo = document.getElementById("correo").value.trim();
        const contrasena = document.getElementById("contrasena").value.trim();

        if (correo === "" || contrasena === "") {
            alert("Debe completar todos los campos.");
            return;
        }

        alert("Datos recibidos. La autenticación será integrada posteriormente con PHP.");

    });

});