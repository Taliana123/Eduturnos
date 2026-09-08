<?php

require_once "_helpers.php";

exigirRol([
    "Super Admin",
    "Coordinador",
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

if ($cita["estado"] !== "Pendiente") {
    responder(
        false,
        "Solo se pueden confirmar citas pendientes.",
        [],
        409
    );
}

$idEstado = obtenerEstadoId(
    $conexion,
    "Confirmada"
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
    "Pendiente",
    "Confirmada",
    "Citación confirmada."
);

notificarCita(
    $conexion,
    $idCita,
    "Citación confirmada",
    "La citación ha sido confirmada."
);

registrarAuditoria(
    $conexion,
    "Confirmar citación",
    "citas",
    $idCita,
    "Citación confirmada."
);

responder(
    true,
    "Citación confirmada correctamente."
);