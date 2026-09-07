document.addEventListener("DOMContentLoaded", () => {

    const formLogin =
        document.getElementById("formLogin");

    const formRegistro =
        document.getElementById("formRegistro");

    const formVerificar =
        document.getElementById("formVerificar");


    if (formLogin) {

        formLogin.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();

                const datos =
                    new FormData(formLogin);

                const mensaje =
                    document.getElementById(
                        "mensajeLogin"
                    );

                mensaje.textContent =
                    "Iniciando sesión...";

                try {

                    const respuesta =
                        await fetch(
                            "api/login.php",
                            {
                                method: "POST",
                                body: datos
                            }
                        );

                    const resultado =
                        await respuesta.json();

                    if (!resultado.ok) {

                        mensaje.textContent =
                            resultado.mensaje;

                        return;
                    }

                    sessionStorage.setItem(
                        "usuario",
                        JSON.stringify(
                            resultado.datos.usuario
                        )
                    );

                    window.location.href =
                        "dashboard.html";

                } catch (error) {

                    mensaje.textContent =
                        "No fue posible conectarse con el servidor.";
                }

            }
        );

    }


    if (formRegistro) {

        formRegistro.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();

                const datos =
                    new FormData(formRegistro);

                const mensaje =
                    document.getElementById(
                        "mensajeRegistro"
                    );

                mensaje.textContent =
                    "Registrando usuario...";

                try {

                    const respuesta =
                        await fetch(
                            "api/registro.php",
                            {
                                method: "POST",
                                body: datos
                            }
                        );

                    const resultado =
                        await respuesta.json();

                    if (!resultado.ok) {

                        mensaje.textContent =
                            resultado.mensaje;

                        return;
                    }

                    sessionStorage.setItem(
                        "documentoVerificacion",
                        resultado.datos.documento
                    );

                    alert(
                        "Cuenta creada.\n\n" +
                        "Código de desarrollo: " +
                        resultado.datos.codigo_desarrollo
                    );

                    window.location.href =
                        "verificar.html";

                } catch (error) {

                    mensaje.textContent =
                        "No fue posible registrar la cuenta.";
                }

            }
        );

    }


    if (formVerificar) {

        formVerificar.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();

                const datos =
                    new FormData(formVerificar);

                const mensaje =
                    document.getElementById(
                        "mensajeVerificar"
                    );

                mensaje.textContent =
                    "Verificando...";

                try {

                    const respuesta =
                        await fetch(
                            "api/verificar.php",
                            {
                                method: "POST",
                                body: datos
                            }
                        );

                    const resultado =
                        await respuesta.json();

                    if (!resultado.ok) {

                        mensaje.textContent =
                            resultado.mensaje;

                        return;
                    }

                    mensaje.textContent =
                        "Cuenta verificada correctamente.";

                    setTimeout(() => {

                        window.location.href =
                            "login.html";

                    }, 1200);

                } catch (error) {

                    mensaje.textContent =
                        "No fue posible verificar la cuenta.";
                }

            }
        );

    }

});


async function cerrarSesion() {

    try {

        await fetch(
            "api/logout.php",
            {
                method: "POST"
            }
        );

    } catch (error) {

        console.error(error);

    }

    sessionStorage.clear();

    window.location.href =
        "login.html";
}