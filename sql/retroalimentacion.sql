CREATE TABLE IF NOT EXISTS retroalimentacion_usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_institucion INT NULL,
    tipo ENUM('Me gusta','No me gusta','Queja','Idea de mejora') NOT NULL,
    asunto VARCHAR(120) NOT NULL,
    comentario TEXT NOT NULL,
    estado ENUM('Nueva','En revisión','Atendida') NOT NULL DEFAULT 'Nueva',
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_institucion) REFERENCES instituciones(id) ON DELETE SET NULL,
    INDEX idx_retro_institucion_estado_fecha (id_institucion, estado, fecha_creacion),
    INDEX idx_retro_usuario_fecha (id_usuario, fecha_creacion)
) ENGINE=InnoDB;
