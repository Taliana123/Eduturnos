<?php

session_start();

require_once "../config/conexion.php";

if (!isset($_SESSION["usuario_id"])) {
    die("Acceso no autorizado.");
}

$id_cita = $_POST["id_cita"] ?? "";
$fecha = $_POST["fecha"] ?? "";
$hora = $_POST["hora"] ?? "";
$lugar = $_POST["lugar"] ?? "";
$observaciones = $_POST["observaciones"] ?? "";

if (
    $id_cita == "" ||
    $fecha == "" ||
    $hora == "" ||
    $lugar == ""
) {
    die("Complete todos los campos obligatorios.");
}

/* Obtener información anterior */

$sql = "SELECT ec.nombre AS estado_anterior
        FROM citas c
        INNER JOIN estados_cita ec
            ON c.id_estado = ec.id_estado
        WHERE c.id_cita = ?";

$stmt = $conexion->prepare($sql);
$stmt->bind_param("i", $id_cita);
$stmt->execute();

$resultado = $stmt->get_result();

if ($resultado->num_rows == 0) {
    die("La citación no existe.");
}

$cita = $resultado->fetch_assoc();
$estadoAnterior = $cita["estado_anterior"];

/* Actualizar */

$sql = "UPDATE citas
        SET fecha = ?,
            hora = ?,
            lugar = ?,
            observaciones = ?
        WHERE id_cita = ?";

$stmt = $conexion->prepare($sql);

$stmt->bind_param(
    "ssssi",
    $fecha,
    $hora,
    $lugar,
    $observaciones,
    $id_cita
);

if ($stmt->execute()) {

    $sqlSeguimiento = "INSERT INTO seguimiento_citas
    (
        id_cita,
        estado_anterior,
        estado_nuevo,
        observacion,
        usuario_responsable
    )
    VALUES (?, ?, ?, ?, ?)";

    $estadoNuevo = $estadoAnterior;
    $observacion = "Citación modificada.";

    $stmtSeguimiento = $conexion->prepare($sqlSeguimiento);

    $stmtSeguimiento->bind_param(
        "isssi",
        $id_cita,
        $estadoAnterior,
        $estadoNuevo,
        $observacion,
        $_SESSION["usuario_id"]
    );

    $stmtSeguimiento->execute();

    echo "Citación actualizada correctamente.";

} else {

    echo "No se pudo actualizar la citación.";
}

?>