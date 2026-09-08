<?php

require_once "_helpers.php";

exigirRol([
    "Super Admin",
    "Coordinador",
    "Docente"
]);

$desde = $_GET["desde"] ?? "";
$hasta = $_GET["hasta"] ?? "";
$estado = $_GET["estado"] ?? "";
$idDocente = (int)($_GET["id_docente"] ?? 0);
$idMotivo = (int)($_GET["id_motivo"] ?? 0);

$sql = "
    SELECT
        c.id_cita,
        c.fecha,
        c.hora,

        CONCAT(
            e.nombres,
            ' ',
            e.apellidos
        ) AS estudiante,

        CONCAT(
            u.nombres,
            ' ',
            u.apellidos
        ) AS docente,

        a.nombres AS acudiente,
        m.nombre AS motivo,
        ec.nombre AS estado,
        c.lugar,
        c.observaciones

    FROM citas c

    INNER JOIN estudiantes e
        ON c.id_estudiante = e.id_estudiante

    INNER JOIN acudientes a
        ON c.id_acudiente = a.id_acudiente

    INNER JOIN docentes d
        ON c.id_docente = d.id_docente

    INNER JOIN usuarios u
        ON d.id_usuario = u.id_usuario

    INNER JOIN motivos m
        ON c.id_motivo = m.id_motivo

    INNER JOIN estados_cita ec
        ON c.id_estado = ec.id_estado

    WHERE 1 = 1
";

$tipos = "";
$parametros = [];

if ($desde !== "") {
    $sql .= " AND c.fecha >= ?";
    $tipos .= "s";
    $parametros[] = $desde;
}

if ($hasta !== "") {
    $sql .= " AND c.fecha <= ?";
    $tipos .= "s";
    $parametros[] = $hasta;
}

if ($estado !== "") {
    $sql .= " AND ec.nombre = ?";
    $tipos .= "s";
    $parametros[] = $estado;
}

if ($idDocente > 0) {
    $sql .= " AND c.id_docente = ?";
    $tipos .= "i";
    $parametros[] = $idDocente;
}

if ($idMotivo > 0) {
    $sql .= " AND c.id_motivo = ?";
    $tipos .= "i";
    $parametros[] = $idMotivo;
}

$sql .= "
    ORDER BY c.fecha DESC, c.hora DESC
";

$stmt = $conexion->prepare($sql);

if (!empty($parametros)) {
    $stmt->bind_param(
        $tipos,
        ...$parametros
    );
}

$stmt->execute();

$resultado = $stmt->get_result();

$registros = [];

while ($fila = $resultado->fetch_assoc()) {
    $registros[] = $fila;
}

$stmt->close();

/*
 * Resumen
 */
$resumen = [
    "total" => count($registros),
    "pendientes" => 0,
    "confirmadas" => 0,
    "realizadas" => 0,
    "canceladas" => 0,
    "reprogramadas" => 0,
    "no_asistio" => 0,
    "justificadas" => 0
];

foreach ($registros as $registro) {

    switch ($registro["estado"]) {

        case "Pendiente":
            $resumen["pendientes"]++;
            break;

        case "Confirmada":
            $resumen["confirmadas"]++;
            break;

        case "Realizada":
            $resumen["realizadas"]++;
            break;

        case "Cancelada":
            $resumen["canceladas"]++;
            break;

        case "Reprogramada":
            $resumen["reprogramadas"]++;
            break;

        case "No asistió":
            $resumen["no_asistio"]++;
            break;

        case "Justificada":
            $resumen["justificadas"]++;
            break;
    }
}

responder(
    true,
    "Reporte generado.",
    [
        "resumen" => $resumen,
        "registros" => $registros
    ]
);