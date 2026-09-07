USE eduturnos;

CREATE TABLE IF NOT EXISTS motivos (
    id_motivo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    estado TINYINT(1) DEFAULT 1
);

CREATE TABLE IF NOT EXISTS estados_cita (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS citas (
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