<?php

$servidor = "localhost";
$usuario = "root";
$contrasena = "";
$baseDatos = "eduturnos";

$conn = new mysqli(
    $servidor,
    $usuario,
    $contrasena,
    $baseDatos
);

if ($conn->connect_error) {
    die("Error de conexión con la base de datos.");
}

$conn->set_charset("utf8mb4");

?>