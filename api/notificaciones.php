<?php

require_once "_helpers.php";

exigirLogin();

$idUsuario = $_SESSION["usuario"]["id_usuario"];

if ($_SERVER["REQUEST_METHOD"] === "GET") {

    $sql = "
        SELECT
            id_notificacion,
            id_cita,
            titulo,
            mensaje,
            leida,
            fecha_envio
        FROM notificaciones
        WHERE id_usuario = ?
        ORDER BY fecha_envio DESC
    ";

    $stmt = $conexion->prepare($sql);

    $stmt->bind_param(
        "i",
        $idUsuario
    );

    $stmt->execute();

    $resultado = $stmt->get_result();

    $notificaciones = [];

    while ($fila = $resultado->fetch_assoc()) {
        $notificaciones[] = $fila;
    }

    $stmt->close();

    responder(
        true,
        "Notificaciones consultadas.",
        $notificaciones
    );
}

if ($_SERVER["REQUEST_METHOD"] === "POST") {

    $idNotificacion = (int)(
        $_POST["id_notificacion"] ?? 0
    );

    if (!$idNotificacion) {
        responder(
            false,
            "Debe indicar la notificación.",
            [],
            400
        );
    }

    $stmt = $conexion->prepare(
        "UPDATE notificaciones
         SET leida = 1
         WHERE id_notificacion = ?
           AND id_usuario = ?"
    );

    $stmt->bind_param(
        "ii",
        $idNotificacion,
        $idUsuario
    );

    $stmt->execute();
    $stmt->close();

    responder(
        true,
        "Notificación marcada como leída."
    );
}