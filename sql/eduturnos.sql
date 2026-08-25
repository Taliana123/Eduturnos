CREATE DATABASE IF NOT EXISTS eduturnos;

USE eduturnos;

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    estado VARCHAR(20) NOT NULL
);

CREATE TABLE estudiantes (
    id_estudiante INT AUTO_INCREMENT PRIMARY KEY,
    documento VARCHAR(20) NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    grado VARCHAR(20),
    grupo VARCHAR(20)
);

CREATE TABLE acudientes (
    id_acudiente INT AUTO_INCREMENT PRIMARY KEY,
    documento VARCHAR(20) NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100)
);

CREATE TABLE docentes (
    id_docente INT AUTO_INCREMENT PRIMARY KEY,
    documento VARCHAR(20) NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(100)
);

CREATE TABLE motivos (
    id_motivo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE estados (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE citas (
    id_cita INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_acudiente INT NOT NULL,
    id_docente INT NOT NULL,
    id_motivo INT NOT NULL,
    id_estado INT NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    observaciones TEXT,

    FOREIGN KEY (id_estudiante)
        REFERENCES estudiantes(id_estudiante),

    FOREIGN KEY (id_acudiente)
        REFERENCES acudientes(id_acudiente),

    FOREIGN KEY (id_docente)
        REFERENCES docentes(id_docente),

    FOREIGN KEY (id_motivo)
        REFERENCES motivos(id_motivo),

    FOREIGN KEY (id_estado)
        REFERENCES estados(id_estado)
);

CREATE TABLE notificaciones (
    id_notificacion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    mensaje TEXT NOT NULL,
    fecha_envio DATETIME,
    estado VARCHAR(30),

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
);