<?php

require_once "_helpers.php";

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    responder(false, "Método no permitido.", [], 405);
}

$documento = trim($_POST["documento"] ?? "");
$codigo = trim($_POST["codigo"] ?? "");

if ($documento === "" || $codigo === "") {
    responder(false, "Documento y código son obligatorios.", [], 400);
}

$sql = "
    SELECT
        u.id_usuario,
        u.verificado,
        c.id_codigo,
        c.codigo,
        c.fecha_expiracion,
        c.utilizado
    FROM usuarios u
    INNER JOIN codigos_verificacion c
        ON u.id_usuario = c.id_usuario
    WHERE u.documento = ?
      AND c.codigo = ?
      AND c.utilizado = 0
    ORDER BY c.id_codigo DESC
    LIMIT 1
";

$stmt = $conexion->prepare($sql);

$stmt->bind_param(
    "ss",
    $documento,
    $codigo
);

$stmt->execute();

$resultado = $stmt->get_result();
$fila = $resultado->fetch_assoc();

$stmt->close();

if (!$fila) {
    responder(false, "Código incorrecto o ya utilizado.", [], 400);
}

if (strtotime($fila["fecha_expiracion"]) < time()) {
    responder(false, "El código ha expirado.", [], 400);
}

$conexion->begin_transaction();

try {

    $stmt = $conexion->prepare(
        "UPDATE usuarios
         SET verificado = 1
         WHERE id_usuario = ?"
    );

    $stmt->bind_param(
        "i",
        $fila["id_usuario"]
    );

    $stmt->execute();
    $stmt->close();

    $stmt = $conexion->prepare(
        "UPDATE codigos_verificacion
         SET utilizado = 1
         WHERE id_codigo = ?"
    );

    $stmt->bind_param(
        "i",
        $fila["id_codigo"]
    );

    $stmt->execute();
    $stmt->close();

    registrarAuditoria(
        $conexion,
        "Verificación de cuenta",
        "usuarios",
        $fila["id_usuario"],
        "Cuenta verificada correctamente."
    );

    $conexion->commit();

    responder(
        true,
        "Cuenta verificada correctamente."
    );

} catch (Throwable $e) {

    $conexion->rollback();

    responder(
        false,
        "No fue posible verificar la cuenta.",
        [],
        500
    );
}