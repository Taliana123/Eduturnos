<?php

session_start();

require_once "../config/conexion.php";

$documento = $_POST["documento"] ?? "";
$contrasena = $_POST["contrasena"] ?? "";

if ($documento == "" || $contrasena == "") {
    die("Debe completar todos los campos.");
}

$sql = "SELECT * FROM usuarios 
        WHERE documento = ? 
        AND estado = 'Activo' 
        LIMIT 1";

$stmt = $conexion->prepare($sql);
$stmt->bind_param("s", $documento);
$stmt->execute();

$resultado = $stmt->get_result();

if ($resultado->num_rows == 0) {
    die("Usuario no encontrado o cuenta inactiva.");
}

$usuario = $resultado->fetch_assoc();

if (!password_verify($contrasena, $usuario["contrasena"])) {
    die("Contraseña incorrecta.");
}

$_SESSION["usuario_id"] = $usuario["id_usuario"];
$_SESSION["rol_id"] = $usuario["id_rol"];
$_SESSION["nombre"] = $usuario["nombres"];

header("Location: ../dashboard.html");
exit();

?>