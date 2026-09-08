<?php

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

require_once __DIR__ . "/../config/conexion.php";

function responder($ok, $mensaje = "", $datos = [], $codigo = 200)
{
    http_response_code($codigo);

    header("Content-Type: application/json; charset=utf-8");

    echo json_encode([
        "ok" => $ok,
        "mensaje" => $mensaje,
        "datos" => $datos
    ], JSON_UNESCAPED_UNICODE);

    exit;
}

function usuarioAutenticado()
{
    return isset($_SESSION["usuario"]);
}

function usuarioActual()
{
    return $_SESSION["usuario"] ?? null;
}

function exigirLogin()
{
    if (!usuarioAutenticado()) {
        responder(false, "Debe iniciar sesión.", [], 401);
    }
}

function tieneRol($roles)
{
    $usuario = usuarioActual();

    if (!$usuario) {
        return false;
    }

    if (!is_array($roles)) {
        $roles = [$roles];
    }

    return in_array($usuario["rol"], $roles, true);
}

function exigirRol($roles)
{
    exigirLogin();

    if (!tieneRol($roles)) {
        responder(false, "No tiene permisos para realizar esta acción.", [], 403);
    }
}

function registrarAuditoria(
    $conexion,
    $accion,
    $tabla = null,
    $registro = null,
    $descripcion = null
) {
    $idUsuario = $_SESSION["usuario"]["id_usuario"] ?? null;

    $stmt = $conexion->prepare(
        "INSERT INTO auditoria
        (id_usuario, accion, tabla_afectada, registro_afectado, descripcion)
        VALUES (?, ?, ?, ?, ?)"
    );

    if (!$stmt) {
        return;
    }

    $stmt->bind_param(
        "issis",
        $idUsuario,
        $accion,
        $tabla,
        $registro,
        $descripcion
    );

    $stmt->execute();
    $stmt->close();
}

function registrarSeguimiento(
    $conexion,
    $idCita,
    $estadoAnterior,
    $estadoNuevo,
    $observacion = ""
) {
    $idUsuario = $_SESSION["usuario"]["id_usuario"] ?? null;

    $stmt = $conexion->prepare(
        "INSERT INTO seguimiento_citas
        (id_cita, estado_anterior, estado_nuevo, observacion, usuario_responsable)
        VALUES (?, ?, ?, ?, ?)"
    );

    if (!$stmt) {
        return;
    }

    $stmt->bind_param(
        "isssi",
        $idCita,
        $estadoAnterior,
        $estadoNuevo,
        $observacion,
        $idUsuario
    );

    $stmt->execute();
    $stmt->close();
}

function crearNotificacion(
    $conexion,
    $idUsuario,
    $idCita,
    $titulo,
    $mensaje
) {
    if (!$idUsuario) {
        return;
    }

    $stmt = $conexion->prepare(
        "INSERT INTO notificaciones
        (id_usuario, id_cita, titulo, mensaje)
        VALUES (?, ?, ?, ?)"
    );

    if (!$stmt) {
        return;
    }

    $stmt->bind_param(
        "iiss",
        $idUsuario,
        $idCita,
        $titulo,
        $mensaje
    );

    $stmt->execute();
    $stmt->close();
}

function obtenerEstadoId($conexion, $nombre)
{
    $stmt = $conexion->prepare(
        "SELECT id_estado
         FROM estados_cita
         WHERE nombre = ?
         LIMIT 1"
    );

    $stmt->bind_param("s", $nombre);
    $stmt->execute();

    $resultado = $stmt->get_result();
    $fila = $resultado->fetch_assoc();

    $stmt->close();

    return $fila["id_estado"] ?? null;
}

function obtenerEstadoNombre($conexion, $idEstado)
{
    $stmt = $conexion->prepare(
        "SELECT nombre
         FROM estados_cita
         WHERE id_estado = ?
         LIMIT 1"
    );

    $stmt->bind_param("i", $idEstado);
    $stmt->execute();

    $resultado = $stmt->get_result();
    $fila = $resultado->fetch_assoc();

    $stmt->close();

    return $fila["nombre"] ?? "";
}

ffunction notificarCita(
    $conexion,
    $idCita,
    $titulo,
    $mensaje
) {
    $sql = "
        SELECT
            au.id_usuario AS id_acudiente_usuario,
            d.id_usuario AS id_docente_usuario
        FROM citas c

        INNER JOIN acudientes a
            ON c.id_acudiente = a.id_acudiente

        LEFT JOIN usuarios au
            ON au.documento = a.documento

        INNER JOIN docentes d
            ON c.id_docente = d.id_docente

        WHERE c.id_cita = ?

        LIMIT 1
    ";

    $stmt = $conexion->prepare($sql);

    if (!$stmt) {
        return;
    }

    $stmt->bind_param("i", $idCita);

    $stmt->execute();

    $resultado = $stmt->get_result();

    $fila = $resultado->fetch_assoc();

    $stmt->close();

    if (!$fila) {
        return;
    }

    // Notificar al acudiente
    if (!empty($fila["id_acudiente_usuario"])) {

        crearNotificacion(
            $conexion,
            $fila["id_acudiente_usuario"],
            $idCita,
            $titulo,
            $mensaje
        );
    }

    // Notificar al docente
    if (!empty($fila["id_docente_usuario"])) {

        crearNotificacion(
            $conexion,
            $fila["id_docente_usuario"],
            $idCita,
            $titulo,
            $mensaje
        );
    }
}