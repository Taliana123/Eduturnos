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
             WHERE id_usuario = ?
             LIMIT 1"
        );

        $stmt->bind_param(
            "i",
            $usuario["id_usuario"]
        );

        $stmt->execute();

        $fila = $stmt->get_result()->fetch_assoc();

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

    case "Estudiante":

        $condiciones[] = "e.documento = ?";
        $parametros[] = $usuario["documento"];
        $tipos .= "s";

        break;
}

if (!empty($condiciones)) {
    $sql .= " WHERE " . implode(" AND ", $condiciones);
}

$sql .= " ORDER BY c.fecha DESC, c.hora DESC";

$stmt = $conexion->prepare($sql);

if (!empty($parametros)) {
    $stmt->bind_param(
        $tipos,
        ...$parametros
    );
}

$stmt->execute();

$resultado = $stmt->get_result();

$citas = [];

while ($fila = $resultado->fetch_assoc()) {
    $citas[] = $fila;
}

$stmt->close();

responder(
    true,
    "Citaciones consultadas.",
    $citas
);