<?php

require_once "_helpers.php";

exigirLogin();

$usuario = usuarioActual();

$sql = "
    SELECT
        c.id_cita,
        c.fecha,
        c.hora,
        c.lugar,
        c.observaciones,
        c.fecha_creacion,

        e.id_estudiante,
        e.codigo_estudiantil,
        e.nombres AS estudiante_nombres,
        e.apellidos AS estudiante_apellidos,

        a.id_acudiente,
        a.nombres AS acudiente_nombres,
        a.apellidos AS acudiente_apellidos,

        d.id_docente,
        du.nombres AS docente_nombres,
        du.apellidos AS docente_apellidos,

        m.nombre AS motivo,
        ec.nombre AS estado

    FROM citas c

    INNER JOIN estudiantes e
        ON c.id_estudiante = e.id_estudiante

    INNER JOIN acudientes a
        ON c.id_acudiente = a.id_acudiente

    INNER JOIN docentes d
        ON c.id_docente = d.id_docente

    INNER JOIN usuarios du
        ON d.id_usuario = du.id_usuario

    INNER JOIN motivos m
        ON c.id_motivo = m.id_motivo

    INNER JOIN estados_cita ec
        ON c.id_estado = ec.id_estado
";

$condiciones = [];
$parametros = [];
$tipos = "";

switch ($usuario["rol"]) {

    case "Docente":

        $condiciones[] = "d.id_usuario = ?";
        $parametros[] = $usuario["id_usuario"];
        $tipos .= "i";

        break;

   case "Acudiente":

    $stmt = $conexion->prepare(
        "SELECT id_acudiente
         FROM acudientes
         WHERE documento = ?
         LIMIT 1"
    );

    if (!$stmt) {
        responder(
            false,
            "Error al consultar el acudiente.",
            [],
            500
        );
    }

    $documentoUsuario = $usuario["documento"];

    $stmt->bind_param(
        "s",
        $documentoUsuario
    );

    $stmt->execute();

    $resultado = $stmt->get_result();

    $fila = $resultado->fetch_assoc();

    $stmt->close();

    if (!$fila) {
        responder(
            true,
            "No hay citas asociadas.",
            []
        );
    }

    $condiciones[] = "c.id_acudiente = ?";

    $parametros[] = $fila["id_acudiente"];

    $tipos .= "i";

    break;