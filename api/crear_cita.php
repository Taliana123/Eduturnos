<?php

session_start();

require_once "../config/conexion.php";

if (!isset($_SESSION["usuario_id"])) {
    die("Acceso no autorizado.");
}

/* =========================
   RECIBIR DATOS
========================= */

$id_estudiante = $_POST["id_estudiante"] ?? "";
$id_acudiente = $_POST["id_acudiente"] ?? "";
$id_docente = $_POST["id_docente"] ?? "";
$id_motivo = $_POST["id_motivo"] ?? "";
$fecha = $_POST["fecha"] ?? "";
$hora = $_POST["hora"] ?? "";
$lugar = $_POST["lugar"] ?? "";
$observaciones = $_POST["observaciones"] ?? "";

/* =========================
   VALIDAR CAMPOS
========================= */

if (
    $id_estudiante == "" ||
    $id_acudiente == "" ||
    $id_docente == "" ||
    $id_motivo == "" ||
    $fecha == "" ||
    $hora == "" ||
    $lugar == ""
) {
    die("Todos los campos obligatorios deben estar completos.");
}

/* =========================
   VERIFICAR ESTUDIANTE
========================= */

$sql = "SELECT id_estudiante
        FROM estudiantes
        WHERE id_estudiante = ?
        AND estado = 'Activo'";

$stmt = $conexion->prepare($sql);
$stmt->bind_param("i", $id_estudiante);
$stmt->execute();

$resultado = $stmt->get_result();

if ($resultado->num_rows == 0) {
    die("El estudiante no existe o está inactivo.");
}

/* =========================
   VERIFICAR ACUDIENTE
========================= */

$sql = "SELECT id_acudiente
        FROM acudientes
        WHERE id_acudiente = ?
        AND estado = 1";

$stmt = $conexion->prepare($sql);
$stmt->bind_param("i", $id_acudiente);
$stmt->execute();

$resultado = $stmt->get_result();

if ($resultado->num_rows == 0) {
    die("El acudiente no existe o está inactivo.");
}

/* =========================
   VERIFICAR RELACIÓN
========================= */

$sql = "SELECT *
        FROM estudiante_acudiente
        WHERE id_estudiante = ?
        AND id_acudiente = ?";

$stmt = $conexion->prepare($sql);
$stmt->bind_param(
    "ii",
    $id_estudiante,
    $id_acudiente
);

$stmt->execute();

$resultado = $stmt->get_result();

if ($resultado->num_rows == 0) {
    die("El acudiente no está relacionado con el estudiante.");
}

/* =========================
   VERIFICAR DOCENTE
========================= */

$sql = "SELECT id_docente
        FROM docentes
        WHERE id_docente = ?
        AND estado = 1";

$stmt = $conexion->prepare($sql);
$stmt->bind_param("i", $id_docente);
$stmt->execute();

$resultado = $stmt->get_result();

if ($resultado->num_rows == 0) {
    die("El docente no existe o está inactivo.");
}

/* =========================
   VERIFICAR MOTIVO
========================= */

$sql = "SELECT id_motivo
        FROM motivos
        WHERE id_motivo = ?
        AND estado = 1";

$stmt = $conexion->prepare($sql);
$stmt->bind_param("i", $id_motivo);
$stmt->execute();

$resultado = $stmt->get_result();

if ($resultado->num_rows == 0) {
    die("El motivo seleccionado no existe.");
}

/* =========================
   OBTENER ESTADO PENDIENTE
========================= */

$sql = "SELECT id_estado
        FROM estados_cita
        WHERE nombre = 'Pendiente'
        LIMIT 1";

$resultado = $conexion->query($sql);

if ($resultado->num_rows == 0) {
    die("No existe el estado Pendiente.");
}

$estado = $resultado->fetch_assoc();
$id_estado = $estado["id_estado"];

/* =========================
   EVITAR CITA DUPLICADA
========================= */

$sql = "SELECT id_cita
        FROM citas
        WHERE id_estudiante = ?
        AND id_docente = ?
        AND fecha = ?
        AND hora = ?
        AND id_estado != (
            SELECT id_estado
            FROM estados_cita
            WHERE nombre = 'Cancelada'
        )";

$stmt = $conexion->prepare($sql);

$stmt->bind_param(
    "iiss",
    $id_estudiante,
    $id_docente,
    $fecha,
    $hora
);

$stmt->execute();

$resultado = $stmt->get_result();

if ($resultado->num_rows > 0) {
    die("Ya existe una citación para este estudiante, docente, fecha y hora.");
}

/* =========================
   CREAR CITACIÓN
========================= */

$sql = "INSERT INTO citas
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
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)";

$stmt = $conexion->prepare($sql);

$stmt->bind_param(
    "iiiiissss",
    $id_estudiante,
    $id_acudiente,
    $id_docente,
    $id_motivo,
    $id_estado,
    $fecha,
    $hora,
    $lugar,
    $observaciones
);

if ($stmt->execute()) {

    $id_cita = $conexion->insert_id;

    /* Registrar seguimiento */

    $sqlSeguimiento = "INSERT INTO seguimiento_citas
    (
        id_cita,
        estado_anterior,
        estado_nuevo,
        observacion,
        usuario_responsable
    )
    VALUES (?, NULL, 'Pendiente', 'Citación creada', ?)";

    $stmtSeguimiento = $conexion->prepare($sqlSeguimiento);

    $stmtSeguimiento->bind_param(
        "ii",
        $id_cita,
        $_SESSION["usuario_id"]
    );

    $stmtSeguimiento->execute();

    echo "Citación creada correctamente.";

} else {

    echo "No fue posible crear la citación.";
}

?>