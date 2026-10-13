USE eduturnos;

CREATE TABLE IF NOT EXISTS directorio_institucional (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NULL UNIQUE,
    id_rol INT NOT NULL,
    rol_nombre VARCHAR(80) NOT NULL,
    tipo_documento VARCHAR(10) NOT NULL DEFAULT 'CC',
    documento VARCHAR(30) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    fecha_vinculacion DATETIME NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    FOREIGN KEY(id_rol) REFERENCES roles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_directorio_rol ON directorio_institucional(rol_nombre, estado);
