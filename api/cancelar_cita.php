<?php

session_start();

require_once "../config/conexion.php";

if (!isset($_SESSION["usuario_id"])) {
    die("Acceso no autorizado.");
}

$id_cita = $_POST["id_cita"] ?? "";

if ($id_cita == "") {
    die("Citación no válida.");
}

/* Buscar estado actual */

$sql = "SELECT
            c.id_estado,
            ec.nombre AS estado_actual
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

$estadoAnterior = $cita["estado_actual"];

/* Buscar estado Cancelada */

$sql = "SELECT id_estado
        FROM estados_cita
        WHERE nombre = 'Cancelada'
        LIMIT 1";

$resultado = $conexion->query($sql);

if ($resultado->num_rows == 0) {
    die("No existe el estado Cancelada.");
}

$estado = $resultado->fetch_assoc();

$id_estado_cancelada = $estado["id_estado"];

/* Actualizar estado */

$sql = "UPDATE citas
        SET id_estado = ?
        WHERE id_cita = ?";

$stmt = $conexion->prepare($sql);

$stmt->bind_param(
    "ii",
    $id_estado_cancelada,
    $id_cita
);

if ($stmt->execute()) {

    /* Guardar historial */

    $sqlSeguimiento = "INSERT INTO seguimiento_citas
    (
        id_cita,
        estado_anterior,
        estado_nuevo,
        observacion,
        usuario_responsable
    )
    VALUES (?, ?, 'Cancelada', 'Citación cancelada', ?)";

    $stmtSeguimiento = $conexion->prepare($sqlSeguimiento);

    $stmtSeguimiento->bind_param(
        "isi",
        $id_cita,
        $estadoAnterior,
        $_SESSION["usuario_id"]
    );

    $stmtSeguimiento->execute();

    echo "Citación cancelada correctamente.";

} else {

    echo "No se pudo cancelar la citación.";
}

?>