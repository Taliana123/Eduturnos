<?php

require_once "_helpers.php";

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    responder(false, "Método no permitido.", [], 405);
}

$tipoDocumento = trim($_POST["tipo_documento"] ?? "");
$documento = trim($_POST["documento"] ?? "");
$nombres = trim($_POST["nombres"] ?? "");
$apellidos = trim($_POST["apellidos"] ?? "");
$correo = trim($_POST["correo"] ?? "");
$telefono = trim($_POST["telefono"] ?? "");
$contrasena = $_POST["contrasena"] ?? "";
$confirmar = $_POST["confirmar_contrasena"] ?? "";

if (
    $documento === "" ||
    $nombres === "" ||
    $apellidos === "" ||
    $correo === "" ||
    $contrasena === ""
) {
    responder(false, "Complete todos los campos obligatorios.", [], 400);
}

if (!filter_var($correo, FILTER_VALIDATE_EMAIL)) {
    responder(false, "El correo no es válido.", [], 400);
}

if (strlen($contrasena) < 6) {
    responder(false, "La contraseña debe tener mínimo 6 caracteres.", [], 400);
}

if ($contrasena !== $confirmar) {
    responder(false, "Las contraseñas no coinciden.", [], 400);
}

$stmt = $conexion->prepare(
    "SELECT id_usuario
     FROM usuarios
     WHERE documento = ? OR correo = ?
     LIMIT 1"
);

$stmt->bind_param("ss", $documento, $correo);
$stmt->execute();

$resultado = $stmt->get_result();

if ($resultado->num_rows > 0) {
    $stmt->close();

    responder(
        false,
        "El documento o correo ya está registrado.",
        [],
        409
    );
}

$stmt->close();

$stmt = $conexion->prepare(
    "SELECT id_rol
     FROM roles
     WHERE nombre = 'Acudiente'
     LIMIT 1"
);

$stmt->execute();

$resultado = $stmt->get_result();
$rol = $resultado->fetch_assoc();

$stmt->close();

if (!$rol) {
    responder(false, "No existe el rol Acudiente.", [], 500);
}

$idRol = $rol["id_rol"];

$hash = password_hash(
    $contrasena,
    PASSWORD_DEFAULT
);

$conexion->begin_transaction();

try {

    $stmt = $conexion->prepare(
        "INSERT INTO usuarios
        (
            id_rol,
            tipo_documento,
            documento,
            nombres,
            apellidos,
            correo,
            telefono,
            contrasena,
            verificado,
            estado
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 1)"
    );

    $stmt->bind_param(
        "isssssss",
        $idRol,
        $tipoDocumento,
        $documento,
        $nombres,
        $apellidos,
        $correo,
        $telefono,
        $hash
    );

    $stmt->execute();

    $idUsuario = $conexion->insert_id;

    $stmt->close();

    $stmt = $conexion->prepare(
        "INSERT INTO acudientes
        (
            id_usuario,
            documento,
            nombres,
            apellidos,
            telefono,
            correo,
            estado
        )
        VALUES (?, ?, ?, ?, ?, ?, 1)"
    );

    $stmt->bind_param(
        "isssss",
        $idUsuario,
        $documento,
        $nombres,
        $apellidos,
        $telefono,
        $correo
    );

    $stmt->execute();
    $stmt->close();

    $codigo = (string) random_int(100000, 999999);

    $stmt = $conexion->prepare(
        "INSERT INTO codigos_verificacion
        (
            id_usuario,
            codigo,
            fecha_expiracion,
            utilizado
        )
        VALUES (?, ?, DATE_ADD(NOW(), INTERVAL 15 MINUTE), 0)"
    );

    $stmt->bind_param(
        "is",
        $idUsuario,
        $codigo
    );

    $stmt->execute();
    $stmt->close();

    registrarAuditoria(
        $conexion,
        "Registro de usuario",
        "usuarios",
        $idUsuario,
        "Nuevo usuario registrado."
    );

    $conexion->commit();

    responder(
        true,
        "Registro realizado. Verifique su cuenta.",
        [
            "id_usuario" => $idUsuario,
            "documento" => $documento,
            "codigo_desarrollo" => $codigo
        ]
    );

} catch (Throwable $e) {

    $conexion->rollback();

    responder(
        false,
        "No fue posible completar el registro.",
        [],
        500
    );
}