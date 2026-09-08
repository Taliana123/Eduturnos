document.addEventListener("DOMContentLoaded", () => {

    cargarCatalogos();

    const formulario =
        document.getElementById(
            "formCrearCita"
        );

    if (formulario) {

        formulario.addEventListener(
            "submit",
            crearCita
        );
    }

});


async function cargarCatalogos() {

    await cargarCatalogo(
        "estudiantes",
        "id_estudiante",
        estudiante => {

            return (
                estudiante.codigo_estudiantil +
                " - " +
                estudiante.nombres +
                " " +
                estudiante.apellidos
            );

        }
    );


    await cargarCatalogo(
        "acudientes",
        "id_acudiente",
        acudiente => {

            return (
                acudiente.nombres +
                " " +
                acudiente.apellidos +
                " - " +
                acudiente.documento
            );

        }
    );


    await cargarCatalogo(
        "docentes",
        "id_docente",
        docente => {

            return (
                docente.nombres +
                " " +
                docente.apellidos
            );

        }
    );


    await cargarCatalogo(
        "motivos",
        "id_motivo",
        motivo => motivo.nombre
    );

}


async function cargarCatalogo(
    tipo,
    elementoId,
    texto
) {

    const select =
        document.getElementById(
            elementoId
        );

    if (!select) {
        return;
    }

    try {

        const respuesta =
            await fetch(
                `api/catalogos.php?tipo=${tipo}`
            );

        const resultado =
            await respuesta.json();

        if (!resultado.ok) {
            return;
        }

        resultado.datos.forEach(item => {

            const opcion =
                document.createElement(
                    "option"
                );

            opcion.value =
                item[
                    elementoId
                ];

            opcion.textContent =
                texto(item);

            select.appendChild(opcion);

        });

    } catch (error) {

        console.error(
            "Error cargando catálogo:",
            error
        );
    }
}


async function crearCita(event) {

    event.preventDefault();

    const formulario =
        event.target;

    const datos =
        new FormData(formulario);

    const mensaje =
        document.getElementById(
            "mensajeCita"
        );

    mensaje.textContent =
        "Creando citación...";

    try {

        const respuesta =
            await fetch(
                "api/crear_cita.php",
                {
                    method: "POST",
                    body: datos
                }
            );

        const resultado =
            await respuesta.json();

        mensaje.textContent =
            resultado.mensaje;

        if (resultado.ok) {

            formulario.reset();

        }

    } catch (error) {

        mensaje.textContent =
            "No fue posible crear la citación.";
    }
}