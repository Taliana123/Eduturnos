<?php

session_start();

require_once "../config/conexion.php";

if (!isset($_SESSION["usuario_id"])) {
    die("Acceso no autorizado.");
}

$id_cita = $_POST["id_cita"] ?? 0;

if (!$id_cita) {
    die("Citación no válida.");
}

$sql = "UPDATE citas
        SET id_estado = (
            SELECT id_estado
            FROM estados_cita
            WHERE nombre = 'Confirmada'
        )
        WHERE id_cita = ?";

$stmt = $conexion->prepare($sql);
$stmt->bind_param("i", $id_cita);

if ($stmt->execute()) {
    echo "Citación confirmada.";
} else {
    echo "No se pudo confirmar.";
}

?>