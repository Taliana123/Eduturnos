<?php

require_once "_helpers.php";

exigirLogin();

$idCita = (int)($_GET["id_cita"] ?? 0);

if (!$idCita) {
    responder(
        false,
        "Debe indicar la citación.",
        [],
        400
    );
}

$sql = "
    SELECT
        s.id_seguimiento,
        s.id_cita,
        s.estado_anterior,
        s.estado_nuevo,
        s.observacion,
        s.fecha,
        CONCAT(
            u.nombres,
            ' ',
            u.apellidos
        ) AS usuario
    FROM seguimiento_citas s
    LEFT JOIN usuarios u
        ON s.usuario_responsable = u.id_usuario
    WHERE s.id_cita = ?
    ORDER BY s.fecha DESC
";

$stmt = $conexion->prepare($sql);

$stmt->bind_param(
    "i",
    $idCita
);

$stmt->execute();

$resultado = $stmt->get_result();

$seguimiento = [];

while ($fila = $resultado->fetch_assoc()) {
    $seguimiento[] = $fila;
}

$stmt->close();

responder(
    true,
    "Seguimiento consultado.",
    $seguimiento
);