<?php

require_once "_helpers.php";

exigirRol([
    "Super Admin",
    "Coordinador",
    "Docente",
    "Acudiente"
]);

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    responder(false, "Método no permitido.", [], 405);
}

$idCita = (int)($_POST["id_cita"] ?? 0);
$nuevaFecha = trim($_POST["fecha"] ?? "");
$nuevaHora = trim($_POST["hora"] ?? "");

if (!$idCita || !$nuevaFecha || !$nuevaHora) {
    responder(false, "Datos incompletos.", [], 400);
}

if ($nuevaFecha < date("Y-m-d")) {
    responder(
        false,
        "La nueva fecha no puede ser anterior a hoy.",
        [],
        400
    );
}

$stmt = $conexion->prepare(
    "SELECT
        c.id_docente,
        ec.nombre AS estado
     FROM citas c
     INNER JOIN estados_cita ec
        ON c.id_estado = ec.id_estado
     WHERE c.id_cita = ?
     LIMIT 1"
);

$stmt->bind_param("i", $idCita);
$stmt->execute();

$cita = $stmt->get_result()->fetch_assoc();

$stmt->close();

if (!$cita) {
    responder(false, "La citación no existe.", [], 404);
}

if (
    in_array(
        $cita["estado"],
        ["Cancelada", "Realizada", "Justificada"],
        true
    )
) {
    responder(
        false,
        "Esta citación no puede reprogramarse.",
        [],
        409
    );
}

$stmt = $conexion->prepare(
    "SELECT id_cita
     FROM citas
     WHERE fecha = ?
       AND hora = ?
       AND id_docente = ?
       AND id_cita <> ?
       AND id_estado IN (
           SELECT id_estado
           FROM estados_cita
           WHERE nombre IN (
               'Pendiente',
               'Confirmada',
               'Reprogramada'
           )
       )
     LIMIT 1"
);

$stmt->bind_param(
    "ssii",
    $nuevaFecha,
    $nuevaHora,
    $cita["id_docente"],
    $idCita
);

$stmt->execute();

if ($stmt->get_result()->num_rows > 0) {
    $stmt->close();

    responder(
        false,
        "El nuevo horario ya está ocupado.",
        [],
        409
    );
}

$stmt->close();

$idEstado = obtenerEstadoId(
    $conexion,
    "Reprogramada"
);

$stmt = $conexion->prepare(
    "UPDATE citas
     SET fecha = ?,
         hora = ?,
         id_estado = ?
     WHERE id_cita = ?"
);

$stmt->bind_param(
    "ssii",
    $nuevaFecha,
    $nuevaHora,
    $idEstado,
    $idCita
);

$stmt->execute();
$stmt->close();

registrarSeguimiento(
    $conexion,
    $idCita,
    $cita["estado"],
    "Reprogramada",
    "Nueva fecha: $nuevaFecha $nuevaHora."
);

notificarCita(
    $conexion,
    $idCita,
    "Citación reprogramada",
    "La citación fue reprogramada para $nuevaFecha a las $nuevaHora."
);

registrarAuditoria(
    $conexion,
    "Reprogramar citación",
    "citas",
    $idCita,
    "Citación reprogramada."
);

responder(
    true,
    "Citación reprogramada correctamente."
);