<?php

require_once "_helpers.php";

exigirLogin();

$tipo = $_GET["tipo"] ?? "";

switch ($tipo) {

    case "estudiantes":

        $sql = "
            SELECT
                id_estudiante,
                codigo_estudiantil,
                documento,
                nombres,
                apellidos,
                id_sede,
                id_jornada,
                id_grado,
                id_grupo,
                estado
            FROM estudiantes
            WHERE estado = 'Activo'
            ORDER BY apellidos, nombres
        ";

        $resultado = $conexion->query($sql);

        $datos = [];

        while ($fila = $resultado->fetch_assoc()) {
            $datos[] = $fila;
        }

        responder(true, "Estudiantes encontrados.", $datos);
        break;


    case "acudientes":

        $sql = "
            SELECT
                id_acudiente,
                documento,
                nombres,
                apellidos,
                parentesco,
                telefono,
                correo
            FROM acudientes
            WHERE estado = 1
            ORDER BY apellidos, nombres
        ";

        $resultado = $conexion->query($sql);

        $datos = [];

        while ($fila = $resultado->fetch_assoc()) {
            $datos[] = $fila;
        }

        responder(true, "Acudientes encontrados.", $datos);
        break;


    case "docentes":

        $sql = "
            SELECT
                d.id_docente,
                d.id_usuario,
                u.nombres,
                u.apellidos,
                u.documento
            FROM docentes d
            INNER JOIN usuarios u
                ON d.id_usuario = u.id_usuario
            WHERE d.estado = 1
              AND u.estado = 1
            ORDER BY u.apellidos, u.nombres
        ";

        $resultado = $conexion->query($sql);

        $datos = [];

        while ($fila = $resultado->fetch_assoc()) {
            $datos[] = $fila;
        }

        responder(true, "Docentes encontrados.", $datos);
        break;


    case "motivos":

        $sql = "
            SELECT
                id_motivo,
                nombre
            FROM motivos
            WHERE estado = 1
            ORDER BY nombre
        ";

        $resultado = $conexion->query($sql);

        $datos = [];

        while ($fila = $resultado->fetch_assoc()) {
            $datos[] = $fila;
        }

        responder(true, "Motivos encontrados.", $datos);
        break;


    default:

        responder(
            false,
            "Tipo de catálogo no válido.",
            [],
            400
        );
}