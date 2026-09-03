CREATE DATABASE IF NOT EXISTS eduturnos
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE eduturnos;

CREATE TABLE roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    estado TINYINT(1) DEFAULT 1
);

CREATE TABLE permisos (
    id_permiso INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    estado TINYINT(1) DEFAULT 1
);

CREATE TABLE rol_permiso (
    id_rol INT NOT NULL,
    id_permiso INT NOT NULL,

    PRIMARY KEY (id_rol, id_permiso),

    FOREIGN KEY (id_rol)
        REFERENCES roles(id_rol),

    FOREIGN KEY (id_permiso)
        REFERENCES permisos(id_permiso)
);

CREATE TABLE instituciones (
    id_institucion INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    nit VARCHAR(30),
    estado TINYINT(1) DEFAULT 1
);

CREATE TABLE sedes (
    id_sede INT AUTO_INCREMENT PRIMARY KEY,
    id_institucion INT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    estado TINYINT(1) DEFAULT 1,

    FOREIGN KEY (id_institucion)
        REFERENCES instituciones(id_institucion)
);

CREATE TABLE jornadas (
    id_jornada INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    estado TINYINT(1) DEFAULT 1
);

CREATE TABLE grados (
    id_grado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL,
    estado TINYINT(1) DEFAULT 1
);

CREATE TABLE grupos (
    id_grupo INT AUTO_INCREMENT PRIMARY KEY,
    id_grado INT NOT NULL,
    nombre VARCHAR(20) NOT NULL,
    estado TINYINT(1) DEFAULT 1,

    FOREIGN KEY (id_grado)
        REFERENCES grados(id_grado)
);

CREATE TABLE periodos_academicos (
    id_periodo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    estado TINYINT(1) DEFAULT 1
);

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    id_rol INT NOT NULL,
    documento VARCHAR(30) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(150) UNIQUE,
    telefono VARCHAR(30),
    contrasena VARCHAR(255) NOT NULL,
    verificado TINYINT(1) DEFAULT 0,
    estado TINYINT(1) DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_rol)
        REFERENCES roles(id_rol)
);

CREATE TABLE estudiantes (
    id_estudiante INT AUTO_INCREMENT PRIMARY KEY,
    codigo_estudiantil VARCHAR(30) NOT NULL UNIQUE,
    documento VARCHAR(30) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    id_sede INT NOT NULL,
    id_jornada INT NOT NULL,
    id_grado INT NOT NULL,
    id_grupo INT NOT NULL,
    id_periodo INT,
    estado VARCHAR(30) DEFAULT 'Activo',

    FOREIGN KEY (id_sede)
        REFERENCES sedes(id_sede),

    FOREIGN KEY (id_jornada)
        REFERENCES jornadas(id_jornada),

    FOREIGN KEY (id_grado)
        REFERENCES grados(id_grado),

    FOREIGN KEY (id_grupo)
        REFERENCES grupos(id_grupo),

    FOREIGN KEY (id_periodo)
        REFERENCES periodos_academicos(id_periodo)
);

CREATE TABLE acudientes (
    id_acudiente INT AUTO_INCREMENT PRIMARY KEY,
    documento VARCHAR(30) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    parentesco VARCHAR(50),
    telefono VARCHAR(30),
    correo VARCHAR(150),
    direccion VARCHAR(200),
    estado TINYINT(1) DEFAULT 1
);

CREATE TABLE estudiante_acudiente (
    id_estudiante INT NOT NULL,
    id_acudiente INT NOT NULL,
    principal TINYINT(1) DEFAULT 0,

    PRIMARY KEY (id_estudiante, id_acudiente),

    FOREIGN KEY (id_estudiante)
        REFERENCES estudiantes(id_estudiante),

    FOREIGN KEY (id_acudiente)
        REFERENCES acudientes(id_acudiente)
);

CREATE TABLE docentes (
    id_docente INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE,
    id_sede INT NOT NULL,
    id_jornada INT NOT NULL,
    area VARCHAR(100),
    asignatura VARCHAR(100),
    estado TINYINT(1) DEFAULT 1,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    FOREIGN KEY (id_sede)
        REFERENCES sedes(id_sede),

    FOREIGN KEY (id_jornada)
        REFERENCES jornadas(id_jornada)
);

CREATE TABLE asignaciones_docentes (
    id_asignacion INT AUTO_INCREMENT PRIMARY KEY,
    id_docente INT NOT NULL,
    id_grado INT NOT NULL,
    id_grupo INT NOT NULL,
    id_periodo INT,

    FOREIGN KEY (id_docente)
        REFERENCES docentes(id_docente),

    FOREIGN KEY (id_grado)
        REFERENCES grados(id_grado),

    FOREIGN KEY (id_grupo)
        REFERENCES grupos(id_grupo),

    FOREIGN KEY (id_periodo)
        REFERENCES periodos_academicos(id_periodo)
);

CREATE TABLE motivos (
    id_motivo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    estado TINYINT(1) DEFAULT 1
);

CREATE TABLE estados_cita (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
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
    lugar VARCHAR(150),
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_estudiante)
        REFERENCES estudiantes(id_estudiante),

    FOREIGN KEY (id_acudiente)
        REFERENCES acudientes(id_acudiente),

    FOREIGN KEY (id_docente)
        REFERENCES docentes(id_docente),

    FOREIGN KEY (id_motivo)
        REFERENCES motivos(id_motivo),

    FOREIGN KEY (id_estado)
        REFERENCES estados_cita(id_estado)
);

CREATE TABLE seguimiento_citas (
    id_seguimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT NOT NULL,
    estado_anterior VARCHAR(50),
    estado_nuevo VARCHAR(50),
    observacion TEXT,
    usuario_responsable INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_cita)
        REFERENCES citas(id_cita),

    FOREIGN KEY (usuario_responsable)
        REFERENCES usuarios(id_usuario)
);

CREATE TABLE justificaciones (
    id_justificacion INT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT NOT NULL,
    descripcion TEXT NOT NULL,
    estado VARCHAR(30) DEFAULT 'Pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_cita)
        REFERENCES citas(id_cita)
);

CREATE TABLE notificaciones (
    id_notificacion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_cita INT,
    titulo VARCHAR(150) NOT NULL,
    mensaje TEXT NOT NULL,
    leida TINYINT(1) DEFAULT 0,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    FOREIGN KEY (id_cita)
        REFERENCES citas(id_cita)
);

CREATE TABLE codigos_verificacion (
    id_codigo INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    codigo VARCHAR(10) NOT NULL,
    fecha_expiracion DATETIME NOT NULL,
    utilizado TINYINT(1) DEFAULT 0,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
);

CREATE TABLE auditoria (
    id_auditoria INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    accion VARCHAR(100) NOT NULL,
    tabla_afectada VARCHAR(100),
    registro_afectado INT,
    descripcion TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
);

INSERT INTO roles (nombre, descripcion)
VALUES
('Super Admin', 'Administración global del sistema'),
('Coordinador', 'Administración institucional'),
('Docente', 'Gestión de citaciones propias'),
('Acudiente', 'Consulta y gestión de sus citaciones'),
('Estudiante', 'Consulta de citaciones'),
('Invitado', 'Acceso público limitado');

INSERT INTO jornadas (nombre)
VALUES
('Mañana'),
('Tarde'),
('Nocturna');

INSERT INTO estados_cita (nombre)
VALUES
('Pendiente'),
('Confirmada'),
('Realizada'),
('Cancelada'),
('Reprogramada'),
('No asistió'),
('Justificada');

INSERT INTO motivos (nombre)
VALUES
('Académico'),
('Disciplinario'),
('Asistencia'),
('Convivencia'),
('Orientación');

INSERT INTO grados (nombre)
VALUES
('1°'),
('2°'),
('3°'),
('4°'),
('5°'),
('6°'),
('7°'),
('8°'),
('9°'),
('10°'),
('11°');