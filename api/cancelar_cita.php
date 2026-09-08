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

if (!$idCita) {
    responder(false, "Debe indicar la citación.", [], 400);
}

$stmt = $conexion->prepare(
    "SELECT
        c.id_estado,
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
        "La citación ya no puede cancelarse.",
        [],
        409
    );
}

$idEstado = obtenerEstadoId(
    $conexion,
    "Cancelada"
);

$stmt = $conexion->prepare(
    "UPDATE citas
     SET id_estado = ?
     WHERE id_cita = ?"
);

$stmt->bind_param(
    "ii",
    $idEstado,
    $idCita
);

$stmt->execute();
$stmt->close();

registrarSeguimiento(
    $conexion,
    $idCita,
    $cita["estado"],
    "Cancelada",
    "Citación cancelada."
);

notificarCita(
    $conexion,
    $idCita,
    "Citación cancelada",
    "La citación ha sido cancelada."
);

registrarAuditoria(
    $conexion,
    "Cancelar citación",
    "citas",
    $idCita,
    "Citación cancelada."
);

responder(
    true,
    "Citación cancelada correctamente."
);