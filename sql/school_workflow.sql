CREATE TABLE IF NOT EXISTS compromisos_cita (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT NOT NULL,
    descripcion TEXT NOT NULL,
    responsable VARCHAR(150) NOT NULL,
    fecha_limite DATE NOT NULL,
    estado ENUM('Pendiente','Cumplido','Cancelado') NOT NULL DEFAULT 'Pendiente',
    creado_por INT NOT NULL,
    actualizado_por INT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cita) REFERENCES citas(id) ON DELETE RESTRICT,
    FOREIGN KEY (creado_por) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    FOREIGN KEY (actualizado_por) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    INDEX idx_compromiso_plazo (estado, fecha_limite),
    INDEX idx_compromiso_cita (id_cita, estado)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cierres_cita (
    id_cita INT PRIMARY KEY,
    asistencia ENUM('Asistió','No asistió') NOT NULL,
    resultado TEXT NOT NULL,
    cerrado_por INT NOT NULL,
    fecha_cierre DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cita) REFERENCES citas(id) ON DELETE RESTRICT,
    FOREIGN KEY (cerrado_por) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS reprogramaciones_cita (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT NOT NULL,
    fecha_anterior DATE NOT NULL,
    hora_anterior TIME NOT NULL,
    fecha_nueva DATE NOT NULL,
    hora_nueva TIME NOT NULL,
    motivo TEXT NOT NULL,
    realizado_por INT NOT NULL,
    fecha_cambio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cita) REFERENCES citas(id) ON DELETE RESTRICT,
    FOREIGN KEY (realizado_por) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    INDEX idx_reprogramacion_cita (id_cita, fecha_cambio)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS disponibilidad_docente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_docente INT NOT NULL,
    dia_semana TINYINT NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    creado_por INT NOT NULL,
    FOREIGN KEY (id_docente) REFERENCES docentes(id_docente) ON DELETE RESTRICT,
    FOREIGN KEY (creado_por) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    UNIQUE KEY uq_disponibilidad (id_docente, dia_semana, hora_inicio, hora_fin)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS entregas_correo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT NOT NULL,
    id_usuario INT NOT NULL,
    tipo VARCHAR(40) NOT NULL,
    estado ENUM('Pendiente','Enviado','Fallido','Sin correo') NOT NULL DEFAULT 'Pendiente',
    intentos INT NOT NULL DEFAULT 0,
    ultimo_error VARCHAR(150) NULL,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cita) REFERENCES citas(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    UNIQUE KEY uq_entrega_cita (id_cita, id_usuario, tipo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS integraciones_google (
    scope_key VARCHAR(50) PRIMARY KEY,
    tipo ENUM('Institucional','Personal') NOT NULL,
    id_usuario INT NULL,
    correo_google VARCHAR(180) NULL,
    calendar_id VARCHAR(255) NOT NULL DEFAULT 'primary',
    token_cifrado MEDIUMTEXT NOT NULL,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_google_integracion_usuario (id_usuario)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS eventos_google (
    id_cita INT NOT NULL,
    scope_key VARCHAR(50) NOT NULL,
    google_event_id VARCHAR(100) NOT NULL,
    estado ENUM('Sincronizado','Fallido') NOT NULL DEFAULT 'Fallido',
    ultimo_error VARCHAR(180) NULL,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id_cita, scope_key),
    FOREIGN KEY (id_cita) REFERENCES citas(id) ON DELETE CASCADE,
    FOREIGN KEY (scope_key) REFERENCES integraciones_google(scope_key) ON DELETE CASCADE,
    INDEX idx_eventos_google_estado (estado, fecha_actualizacion)
) ENGINE=InnoDB;