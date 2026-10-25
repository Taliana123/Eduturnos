CREATE DATABASE IF NOT EXISTS eduturnos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE eduturnos;

CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS permisos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS rol_permiso (
    id_rol INT NOT NULL,
    id_permiso INT NOT NULL,
    PRIMARY KEY (id_rol, id_permiso),
    FOREIGN KEY (id_rol) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (id_permiso) REFERENCES permisos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS instituciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(180) NOT NULL,
    ciudad VARCHAR(100) NOT NULL DEFAULT 'Ibagué',
    departamento VARCHAR(100) NOT NULL DEFAULT 'Tolima',
    direccion VARCHAR(255) NULL,
    telefono VARCHAR(40) NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    UNIQUE KEY uq_institucion_nombre (nombre)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sedes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_institucion INT NOT NULL,
    nombre VARCHAR(140) NOT NULL,
    direccion VARCHAR(255) NULL,
    codigo_sede CHAR(6) NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    UNIQUE KEY uq_sede_institucion (id_institucion, nombre),
    UNIQUE KEY uq_sede_codigo (id_institucion, codigo_sede),
    FOREIGN KEY (id_institucion) REFERENCES instituciones(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS jornadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    estado TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS grados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE,
    estado TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS grupos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_grado INT NOT NULL,
    nombre VARCHAR(20) NOT NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    UNIQUE KEY uq_grupo (id_grado, nombre),
    FOREIGN KEY (id_grado) REFERENCES grados(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS periodos_academicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 0,
    cerrado TINYINT(1) NOT NULL DEFAULT 0,
    UNIQUE KEY uq_periodo_nombre (nombre),
    CHECK (fecha_fin >= fecha_inicio)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    id_rol INT NOT NULL,
    tipo_documento VARCHAR(20) NOT NULL DEFAULT 'CC',
    documento VARCHAR(30) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(40) NULL,
    password_hash VARCHAR(255) NOT NULL,
    verificado TINYINT(1) NOT NULL DEFAULT 0,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    intentos_fallidos INT NOT NULL DEFAULT 0,
    bloqueado_hasta DATETIME NULL,
    ultimo_acceso DATETIME NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_rol) REFERENCES roles(id) ON DELETE RESTRICT,
    INDEX idx_usuario_correo (correo),
    INDEX idx_usuario_rol (id_rol)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estudiantes (
    id_estudiante INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NULL UNIQUE,
    codigo_estudiantil VARCHAR(40) NOT NULL UNIQUE,
    tipo_documento VARCHAR(20) NOT NULL DEFAULT 'TI',
    documento VARCHAR(30) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    curso VARCHAR(30) NULL,
    id_sede INT NOT NULL,
    id_jornada INT NOT NULL,
    id_grado INT NULL,
    id_grupo INT NULL,
    id_periodo INT NOT NULL,
    estado ENUM('Activo','Retirado') NOT NULL DEFAULT 'Activo',
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    FOREIGN KEY (id_sede) REFERENCES sedes(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_jornada) REFERENCES jornadas(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_grado) REFERENCES grados(id) ON DELETE SET NULL,
    FOREIGN KEY (id_grupo) REFERENCES grupos(id) ON DELETE SET NULL,
    FOREIGN KEY (id_periodo) REFERENCES periodos_academicos(id) ON DELETE RESTRICT,
    INDEX idx_estudiante_nombre (apellidos, nombres),
    INDEX idx_estudiante_sede (id_sede)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS acudientes (
    id_acudiente INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NULL UNIQUE,
    tipo_documento VARCHAR(20) NOT NULL DEFAULT 'CC',
    documento VARCHAR(30) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    telefono VARCHAR(40) NULL,
    correo VARCHAR(150) NULL,
    direccion VARCHAR(255) NULL,
    barrio VARCHAR(100) NULL,
    municipio VARCHAR(100) DEFAULT 'Ibagué',
    estado TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    INDEX idx_acudiente_correo (correo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estudiante_acudiente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_acudiente INT NOT NULL,
    parentesco VARCHAR(60) NOT NULL,
    principal TINYINT(1) NOT NULL DEFAULT 0,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    UNIQUE KEY uq_est_acu (id_estudiante, id_acudiente),
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    FOREIGN KEY (id_acudiente) REFERENCES acudientes(id_acudiente) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS docentes (
    id_docente INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NULL UNIQUE,
    tipo_documento VARCHAR(20) NOT NULL DEFAULT 'CC',
    documento VARCHAR(30) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo_institucional VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(40) NULL,
    id_sede INT NOT NULL,
    id_jornada INT NOT NULL,
    area VARCHAR(100) NULL,
    asignatura VARCHAR(100) NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    FOREIGN KEY (id_sede) REFERENCES sedes(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_jornada) REFERENCES jornadas(id) ON DELETE RESTRICT,
    INDEX idx_docente_sede (id_sede)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS asignaciones_docentes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_docente INT NOT NULL,
    id_estudiante INT NULL,
    id_grupo INT NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (id_docente) REFERENCES docentes(id_docente) ON DELETE CASCADE,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    FOREIGN KEY (id_grupo) REFERENCES grupos(id) ON DELETE CASCADE,
    CHECK (id_estudiante IS NOT NULL OR id_grupo IS NOT NULL),
    UNIQUE KEY uq_asig_est (id_docente, id_estudiante),
    INDEX idx_asig_grupo (id_docente, id_grupo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS motivos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estados_cita (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(40) NOT NULL UNIQUE,
    estado TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS directorio_institucional (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NULL UNIQUE,
    id_rol INT NOT NULL,
    tipo_documento VARCHAR(20) NOT NULL DEFAULT 'CC',
    documento VARCHAR(30) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo_institucional VARCHAR(150) NOT NULL UNIQUE,
    id_sede INT NOT NULL,
    id_jornada INT NULL,
    codigo_institucional_hash VARCHAR(255) NOT NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    fecha_vinculacion DATETIME NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    FOREIGN KEY (id_rol) REFERENCES roles(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_sede) REFERENCES sedes(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_jornada) REFERENCES jornadas(id) ON DELETE SET NULL,
    INDEX idx_directorio_rol_sede (id_rol, id_sede, estado)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS citas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_acudiente INT NOT NULL,
    id_docente INT NOT NULL,
    id_motivo INT NOT NULL,
    id_estado INT NOT NULL,
    id_periodo INT NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    lugar VARCHAR(150) NOT NULL,
    observaciones TEXT NULL,
    creado_por INT NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    recordatorio_24h_enviado TINYINT(1) NOT NULL DEFAULT 0,
    recordatorio_2h_enviado TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE RESTRICT,
    FOREIGN KEY (id_acudiente) REFERENCES acudientes(id_acudiente) ON DELETE RESTRICT,
    FOREIGN KEY (id_docente) REFERENCES docentes(id_docente) ON DELETE RESTRICT,
    FOREIGN KEY (id_motivo) REFERENCES motivos(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_estado) REFERENCES estados_cita(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_periodo) REFERENCES periodos_academicos(id) ON DELETE RESTRICT,
    FOREIGN KEY (creado_por) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    INDEX idx_cita_fecha (fecha, hora),
    INDEX idx_cita_estudiante (id_estudiante, fecha),
    INDEX idx_cita_docente (id_docente, fecha),
    UNIQUE KEY uq_cita_docente_hora (id_docente, fecha, hora),
    UNIQUE KEY uq_cita_estudiante_hora (id_estudiante, fecha, hora),
    UNIQUE KEY uq_cita_acudiente_hora (id_acudiente, fecha, hora),
    INDEX idx_cita_recordatorios (fecha, hora, recordatorio_24h_enviado, recordatorio_2h_enviado)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS solicitudes_cita (
    id INT AUTO_INCREMENT PRIMARY KEY,
    solicitante_usuario_id INT NOT NULL,
    tipo_solicitante ENUM('Acudiente','Docente') NOT NULL,
    id_estudiante INT NOT NULL,
    id_acudiente INT NULL,
    id_docente INT NOT NULL,
    id_motivo INT NOT NULL,
    fecha_solicitada DATE NOT NULL,
    hora_solicitada TIME NOT NULL,
    fecha_propuesta DATE NULL,
    hora_propuesta TIME NULL,
    lugar VARCHAR(150) NULL,
    observaciones TEXT NULL,
    respuesta TEXT NULL,
    estado ENUM('Pendiente','Propuesta','Aceptada','Rechazada','Cancelada') NOT NULL DEFAULT 'Pendiente',
    revisado_por INT NULL,
    cita_id INT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_revision DATETIME NULL,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (solicitante_usuario_id) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE RESTRICT,
    FOREIGN KEY (id_acudiente) REFERENCES acudientes(id_acudiente) ON DELETE SET NULL,
    FOREIGN KEY (id_docente) REFERENCES docentes(id_docente) ON DELETE RESTRICT,
    FOREIGN KEY (id_motivo) REFERENCES motivos(id) ON DELETE RESTRICT,
    FOREIGN KEY (revisado_por) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    FOREIGN KEY (cita_id) REFERENCES citas(id) ON DELETE SET NULL,
    INDEX idx_solicitud_estado (estado, fecha_creacion),
    INDEX idx_solicitud_solicitante (solicitante_usuario_id, estado),
    INDEX idx_solicitud_docente (id_docente, fecha_solicitada, hora_solicitada)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS solicitudes_reprogramacion_cita (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT NOT NULL,
    solicitante_usuario_id INT NOT NULL,
    creador_usuario_id INT NOT NULL,
    fecha_anterior DATE NOT NULL,
    hora_anterior TIME NOT NULL,
    fecha_solicitada DATE NOT NULL,
    hora_solicitada TIME NOT NULL,
    motivo TEXT NOT NULL,
    respuesta TEXT NULL,
    estado ENUM('Pendiente','Aceptada','Rechazada') NOT NULL DEFAULT 'Pendiente',
    revisado_por INT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_revision DATETIME NULL,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cita) REFERENCES citas(id) ON DELETE RESTRICT,
    FOREIGN KEY (solicitante_usuario_id) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    FOREIGN KEY (creador_usuario_id) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    FOREIGN KEY (revisado_por) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    INDEX idx_solicitud_reprogramacion_cita (id_cita, estado),
    INDEX idx_solicitud_reprogramacion_creador (creador_usuario_id, estado, fecha_creacion),
    INDEX idx_solicitud_reprogramacion_solicitante (solicitante_usuario_id, fecha_creacion)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS seguimiento_citas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT NOT NULL,
    estado_actual VARCHAR(40) NOT NULL,
    asistencia ENUM('Pendiente','Asistió','No asistió') NOT NULL DEFAULT 'Pendiente',
    observaciones TEXT NULL,
    fecha_seguimiento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    realizado_por INT NOT NULL,
    FOREIGN KEY (id_cita) REFERENCES citas(id) ON DELETE CASCADE,
    FOREIGN KEY (realizado_por) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    INDEX idx_seg_cita (id_cita, fecha_seguimiento)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS justificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT NOT NULL,
    motivo TEXT NOT NULL,
    estado ENUM('Pendiente','Aceptada','Rechazada') NOT NULL DEFAULT 'Pendiente',
    fecha_solicitud DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revisado_por INT NULL,
    fecha_revision DATETIME NULL,
    FOREIGN KEY (id_cita) REFERENCES citas(id) ON DELETE CASCADE,
    FOREIGN KEY (revisado_por) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS notificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    mensaje TEXT NOT NULL,
    tipo VARCHAR(50) NOT NULL DEFAULT 'Sistema',
    leida TINYINT(1) NOT NULL DEFAULT 0,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_notif_usuario_fecha (id_usuario, leida, fecha_creacion)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS codigos_verificacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    codigo VARCHAR(10) NOT NULL,
    fecha_expiracion DATETIME NOT NULL,
    usado TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS control_acceso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    clave_hash CHAR(64) NOT NULL UNIQUE,
    intentos INT NOT NULL DEFAULT 0,
    bloqueado_hasta DATETIME NULL,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_control_bloqueo (bloqueado_hasta)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tokens_recuperacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    token_hash CHAR(64) NOT NULL UNIQUE,
    codigo_hash CHAR(64) NULL,
    intentos INT NOT NULL DEFAULT 0,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion DATETIME NOT NULL,
    usado TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_token_exp (fecha_expiracion, usado)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NULL,
    accion VARCHAR(120) NOT NULL,
    modulo VARCHAR(80) NOT NULL,
    registro_id INT NULL,
    detalle VARCHAR(255) NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    INDEX idx_auditoria_fecha (fecha_creacion)
) ENGINE=InnoDB;

INSERT IGNORE INTO roles (nombre, descripcion) VALUES
('Super Admin','Acceso completo del sistema'),
('Administrador / Coordinador','Administración académica y citaciones'),
('Docente','Gestión de estudiantes asignados y citaciones'),
('Acudiente','Consulta y confirmación de citaciones'),
('Estudiante','Consulta de sus citaciones'),
('Rector','Dirección y consulta institucional');

INSERT IGNORE INTO permisos (nombre, descripcion) VALUES
('usuarios.gestionar','Gestionar usuarios'),
('academico.gestionar','Gestionar información académica'),
('estudiantes.gestionar','Gestionar estudiantes'),
('acudientes.gestionar','Gestionar acudientes'),
('docentes.gestionar','Gestionar docentes'),
('citaciones.gestionar','Gestionar citaciones'),
('seguimiento.gestionar','Gestionar seguimiento'),
('reportes.ver','Ver reportes'),
('auditoria.ver','Ver auditoría'),
('periodos.cerrar','Cerrar periodos');

INSERT IGNORE INTO instituciones (nombre, ciudad, departamento)
VALUES ('Institución Educativa José Joaquín Flórez Hernández','Ibagué','Tolima');

INSERT INTO sedes (id_institucion, nombre, direccion, codigo_sede, estado)
SELECT i.id, x.nombre, x.direccion, x.codigo_sede, 1
FROM instituciones i
JOIN (
    SELECT 'Sede Principal (Las Américas)' AS nombre, 'Ciudadela Las Américas, sector Picaleña (Cra. 15A Sur #2-01)' AS direccion, '238596' AS codigo_sede
    UNION ALL SELECT 'Sede Arboleda Campestre', 'Calle 152 #21 Sur - 22, urbanización Arboleda Campestre', '418257'
    UNION ALL SELECT 'Sede Picaleña', 'Barrio Picaleña, sobre la vía nacional', '724305'
    UNION ALL SELECT 'Sede Bello Horizonte', 'Barrio Bello Horizonte (Km 3 vía Picaleña)', '351864'
    UNION ALL SELECT 'Sede Secundino Porras Cruz', 'Zona sur de Ibagué, parte alta del barrio Picaleña', '563812'
    UNION ALL SELECT 'Sede San Francisco Club', 'Calle 113 con Carrera 48 Sur', '896421'
    UNION ALL SELECT 'Sede San Martín', 'Vereda San Martín', '602137'
) x ON 1=1
ON DUPLICATE KEY UPDATE direccion=VALUES(direccion), codigo_sede=VALUES(codigo_sede), estado=1;

INSERT IGNORE INTO jornadas(nombre) VALUES ('Mañana'),('Tarde'),('Noche');
INSERT IGNORE INTO grados(nombre) VALUES ('1'),('2'),('3'),('4'),('5'),('6'),('7'),('8'),('9'),('10'),('11');

INSERT IGNORE INTO grupos(id_grado,nombre)
SELECT g.id, x.nombre FROM grados g CROSS JOIN (
    SELECT '1' nombre UNION ALL SELECT '2' UNION ALL SELECT '3' UNION ALL SELECT '4' UNION ALL SELECT '5' UNION ALL SELECT '6'
) x;

INSERT IGNORE INTO periodos_academicos(nombre,fecha_inicio,fecha_fin,activo,cerrado)
VALUES ('Periodo académico 2026','2026-01-01','2026-11-30',1,0);

INSERT IGNORE INTO motivos(nombre,descripcion) VALUES
('Bajo rendimiento','Seguimiento académico'),('Convivencia','Situación de convivencia'),
('Inasistencia','Inasistencias reiteradas'),('Incumplimiento','Incumplimiento de compromisos'),('Otro','Otro motivo');

INSERT IGNORE INTO estados_cita(nombre,estado) VALUES
('Pendiente',1),('Confirmada',1),('Realizada',1),('Cancelada',1),('Reprogramada',1),('No asistió',1),('Justificada',1);

INSERT IGNORE INTO rol_permiso(id_rol,id_permiso)
SELECT r.id,p.id FROM roles r CROSS JOIN permisos p WHERE r.nombre='Super Admin';
INSERT IGNORE INTO rol_permiso(id_rol,id_permiso)
SELECT r.id,p.id FROM roles r JOIN permisos p ON p.nombre IN ('academico.gestionar','estudiantes.gestionar','acudientes.gestionar','docentes.gestionar','citaciones.gestionar','seguimiento.gestionar','reportes.ver') WHERE r.nombre='Administrador / Coordinador';
INSERT IGNORE INTO rol_permiso(id_rol,id_permiso)
SELECT r.id,p.id FROM roles r JOIN permisos p ON p.nombre IN ('estudiantes.gestionar','citaciones.gestionar','seguimiento.gestionar') WHERE r.nombre='Docente';
INSERT IGNORE INTO rol_permiso(id_rol,id_permiso)
SELECT r.id,p.id FROM roles r JOIN permisos p ON p.nombre IN ('academico.gestionar','estudiantes.gestionar','acudientes.gestionar','docentes.gestionar','citaciones.gestionar','seguimiento.gestionar','reportes.ver','auditoria.ver','periodos.cerrar') WHERE r.nombre='Rector';
