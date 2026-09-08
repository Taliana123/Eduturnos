<?php

require_once "_helpers.php";

exigirRol([
    "Super Admin",
    "Coordinador",
    "Docente"
]);

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    responder(false, "Método no permitido.", [], 405);
}

$idCita = (int)($_POST["id_cita"] ?? 0);
$fecha = trim($_POST["fecha"] ?? "");
$hora = trim($_POST["hora"] ?? "");
$lugar = trim($_POST["lugar"] ?? "");
$observaciones = trim($_POST["observaciones"] ?? "");

if (!$idCita || !$fecha || !$hora) {
    responder(false, "Datos incompletos.", [], 400);
}

if ($fecha < date("Y-m-d")) {
    responder(false, "La fecha no puede ser anterior a hoy.", [], 400);
}

$stmt = $conexion->prepare(
    "SELECT
        c.id_cita,
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
        "Esta citación ya no puede ser modificada.",
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
    $fecha,
    $hora,
    $cita["id_docente"],
    $idCita
);

$stmt->execute();

if ($stmt->get_result()->num_rows > 0) {
    $stmt->close();

    responder(
        false,
        "Ese horario ya está ocupado.",
        [],
        409
    );
}

$stmt->close();

$stmt = $conexion->prepare(
    "UPDATE citas
     SET fecha = ?,
         hora = ?,
         lugar = ?,
         observaciones = ?
     WHERE id_cita = ?"
);

$stmt->bind_param(
    "ssssi",
    $fecha,
    $hora,
    $lugar,
    $observaciones,
    $idCita
);

$stmt->execute();
$stmt->close();

registrarSeguimiento(
    $conexion,
    $idCita,
    $cita["estado"],
    $cita["estado"],
    "Citación modificada. Nueva fecha: $fecha $hora."
);

notificarCita(
    $conexion,
    $idCita,
    "Citación modificada",
    "La fecha u horario de una citación ha sido modificado."
);

registrarAuditoria(
    $conexion,
    "Editar citación",
    "citas",
    $idCita,
    "Se modificaron los datos de la citación."
);

responder(
    true,
    "Citación actualizada correctamente."
);