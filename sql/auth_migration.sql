USE eduturnos;

CREATE TABLE IF NOT EXISTS codigos_acceso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_rol INT NOT NULL,
    portal VARCHAR(30) NOT NULL,
    documento VARCHAR(30) NULL,
    correo VARCHAR(150) NULL,
    codigo_hash VARCHAR(255) NOT NULL,
    fecha_expiracion DATETIME NOT NULL,
    usado TINYINT(1) NOT NULL DEFAULT 0,
    fecha_uso DATETIME NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(id_rol) REFERENCES roles(id),
    INDEX idx_codigo_acceso_lookup (portal, id_rol, documento, correo, usado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
