<?php

session_start();

require_once "../config/conexion.php";

if (!isset($_SESSION["usuario_id"])) {
    die("Acceso no autorizado.");
}

$fecha_inicio = $_GET["fecha_inicio"] ?? "";
$fecha_fin = $_GET["fecha_fin"] ?? "";
$estado = $_GET["estado"] ?? "";

$sql = "SELECT *
        FROM citas
        WHERE 1=1";

$parametros = [];
$tipos = "";

if ($fecha_inicio != "") {
    $sql .= " AND fecha >= ?";
    $parametros[] = $fecha_inicio;
    $tipos .= "s";
}

if ($fecha_fin != "") {
    $sql .= " AND fecha <= ?";
    $parametros[] = $fecha_fin;
    $tipos .= "s";
}

if ($estado != "") {
    $sql .= " AND id_estado = (
        SELECT id_estado
        FROM estados_cita
        WHERE nombre = ?
    )";

    $parametros[] = $estado;
    $tipos .= "s";
}

$sql .= " ORDER BY fecha DESC, hora DESC";

$stmt = $conexion->prepare($sql);

if (!empty($parametros)) {
    $stmt->bind_param($tipos, ...$parametros);
}

$stmt->execute();

$resultado = $stmt->get_result();

while ($fila = $resultado->fetch_assoc()) {

    echo "<p>";
    echo "Citación #" . $fila["id_cita"];
    echo " - Fecha: " . $fila["fecha"];
    echo " - Hora: " . $fila["hora"];
    echo "</p>";
}

?>