<?php

require_once "_helpers.php";

exigirRol([
    "Super Admin",
    "Coordinador",
    "Docente",
    "Acudiente"
]);

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    responder(false, "Método no permitido.", [], 405);
}

$idEstudiante = (int)($_POST["id_estudiante"] ?? 0);
$idAcudiente = (int)($_POST["id_acudiente"] ?? 0);
$idDocente = (int)($_POST["id_docente"] ?? 0);
$idMotivo = (int)($_POST["id_motivo"] ?? 0);
$fecha = trim($_POST["fecha"] ?? "");
$hora = trim($_POST["hora"] ?? "");
$lugar = trim($_POST["lugar"] ?? "");
$observaciones = trim($_POST["observaciones"] ?? "");

if (
    !$idEstudiante ||
    !$idAcudiente ||
    !$idDocente ||
    !$idMotivo ||
    !$fecha ||
    !$hora
) {
    responder(false, "Complete todos los campos obligatorios.", [], 400);
}

if ($fecha < date("Y-m-d")) {
    responder(false, "No se puede crear una cita en una fecha pasada.", [], 400);
}

/*
 * Verificar estudiante
 */
$stmt = $conexion->prepare(
    "SELECT id_estudiante
     FROM estudiantes
     WHERE id_estudiante = ?
       AND estado = 'Activo'
     LIMIT 1"
);

$stmt->bind_param("i", $idEstudiante);
$stmt->execute();

if ($stmt->get_result()->num_rows === 0) {
    $stmt->close();

    responder(
        false,
        "El estudiante no existe o está retirado.",
        [],
        400
    );
}

$stmt->close();

/*
 * Verificar acudiente
 */
$stmt = $conexion->prepare(
    "SELECT id_acudiente
     FROM acudientes
     WHERE id_acudiente = ?
       AND estado = 1
     LIMIT 1"
);

$stmt->bind_param("i", $idAcudiente);
$stmt->execute();

if ($stmt->get_result()->num_rows === 0) {
    $stmt->close();

    responder(
        false,
        "El acudiente no existe o está inactivo.",
        [],
        400
    );
}

$stmt->close();

/*
 * Verificar relación estudiante/acudiente
 */
$stmt = $conexion->prepare(
    "SELECT id_estudiante
     FROM estudiante_acudiente
     WHERE id_estudiante = ?
       AND id_acudiente = ?
     LIMIT 1"
);

$stmt->bind_param(
    "ii",
    $idEstudiante,
    $idAcudiente
);

$stmt->execute();

if ($stmt->get_result()->num_rows === 0) {
    $stmt->close();

    responder(
        false,
        "El acudiente no está relacionado con el estudiante.",
        [],
        400
    );
}

$stmt->close();

/*
 * Verificar docente
 */
$stmt = $conexion->prepare(
    "SELECT id_docente
     FROM docentes
     WHERE id_docente = ?
       AND estado = 1
     LIMIT 1"
);

$stmt->bind_param("i", $idDocente);
$stmt->execute();

if ($stmt->get_result()->num_rows === 0) {
    $stmt->close();

    responder(
        false,
        "El docente no existe o está inactivo.",
        [],
        400
    );
}

$stmt->close();

/*
 * Verificar motivo
 */
$stmt = $conexion->prepare(
    "SELECT id_motivo
     FROM motivos
     WHERE id_motivo = ?
       AND estado = 1
     LIMIT 1"
);

$stmt->bind_param("i", $idMotivo);
$stmt->execute();

if ($stmt->get_result()->num_rows === 0) {
    $stmt->close();

    responder(
        false,
        "El motivo no existe.",
        [],
        400
    );
}

$stmt->close();

/*
 * Evitar duplicidad
 */
$sql = "
    SELECT id_cita
    FROM citas
    WHERE fecha = ?
      AND hora = ?
      AND id_docente = ?
      AND id_estado IN (
          SELECT id_estado
          FROM estados_cita
          WHERE nombre IN (
              'Pendiente',
              'Confirmada',
              'Reprogramada'
          )
      )
    LIMIT 1
";

$stmt = $conexion->prepare($sql);

$stmt->bind_param(
    "ssi",
    $fecha,
    $hora,
    $idDocente
);

$stmt->execute();

if ($stmt->get_result()->num_rows > 0) {
    $stmt->close();

    responder(
        false,
        "El docente ya tiene una cita en ese horario.",
        [],
        409
    );
}

$stmt->close();

$idEstado = obtenerEstadoId(
    $conexion,
    "Pendiente"
);

$stmt = $conexion->prepare(
    "INSERT INTO citas
    (
        id_estudiante,
        id_acudiente,
        id_docente,
        id_motivo,
        id_estado,
        fecha,
        hora,
        lugar,
        observaciones
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
);

$stmt->bind_param(
    "iiiiissss",
    $idEstudiante,
    $idAcudiente,
    $idDocente,
    $idMotivo,
    $idEstado,
    $fecha,
    $hora,
    $lugar,
    $observaciones
);

if (!$stmt->execute()) {
    $stmt->close();

    responder(
        false,
        "No fue posible crear la citación.",
        [],
        500
    );
}

$idCita = $conexion->insert_id;

$stmt->close();

registrarSeguimiento(
    $conexion,
    $idCita,
    null,
    "Pendiente",
    "Citación creada."
);

notificarCita(
    $conexion,
    $idCita,
    "Nueva citación",
    "Se ha creado una nueva citación para el estudiante."
);

registrarAuditoria(
    $conexion,
    "Crear citación",
    "citas",
    $idCita,
    "Nueva citación creada."
);

responder(
    true,
    "Citación creada correctamente.",
    [
        "id_cita" => $idCita
    ]
);