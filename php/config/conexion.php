<?php

$host = "localhost";
$usuario = "root";
$contrasena = "";
$base_datos = "eduturnos";

$conexion = new mysqli(
    $host,
    $usuario,
    $contrasena,
    $base_datos
);

if ($conexion->connect_error) {
    http_response_code(500);
    die("Error de conexión con la base de datos.");
}

$conexion->set_charset("utf8mb4");