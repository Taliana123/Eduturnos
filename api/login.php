<?php

require_once "_helpers.php";

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    responder(false, "Método no permitido.", [], 405);
}

$documento = trim($_POST["documento"] ?? "");
$contrasena = $_POST["contrasena"] ?? "";

if ($documento === "" || $contrasena === "") {
    responder(false, "Documento y contraseña son obligatorios.", [], 400);
}

$sql = "
    SELECT
        u.id_usuario,
        u.documento,
        u.nombres,
        u.apellidos,
        u.correo,
        u.telefono,
        u.contrasena,
        u.verificado,
        u.estado,
        r.nombre AS rol
    FROM usuarios u
    INNER JOIN roles r
        ON u.id_rol = r.id_rol
    WHERE u.documento = ?
    LIMIT 1
";

$stmt = $conexion->prepare($sql);

$stmt->bind_param(
    "s",
    $documento
);

$stmt->execute();

$resultado = $stmt->get_result();
$usuario = $resultado->fetch_assoc();

$stmt->close();

if (!$usuario) {
    responder(false, "Documento o contraseña incorrectos.", [], 401);
}

if (!password_verify($contrasena, $usuario["contrasena"])) {
    responder(false, "Documento o contraseña incorrectos.", [], 401);
}

if ((int)$usuario["estado"] !== 1) {
    responder(false, "El usuario está inactivo.", [], 403);
}

if ((int)$usuario["verificado"] !== 1) {
    responder(false, "Debe verificar su cuenta antes de ingresar.", [], 403);
}

unset($usuario["contrasena"]);

session_regenerate_id(true);

$_SESSION["usuario"] = $usuario;

registrarAuditoria(
    $conexion,
    "Inicio de sesión",
    "usuarios",
    $usuario["id_usuario"],
    "Inicio de sesión exitoso."
);

responder(
    true,
    "Inicio de sesión correcto.",
    [
        "usuario" => $usuario
    ]
);