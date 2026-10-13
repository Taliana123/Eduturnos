USE eduturnos;

ALTER TABLE docentes
    ADD COLUMN IF NOT EXISTS codigo_institucional_hash VARCHAR(255) NULL;

ALTER TABLE directorio_institucional
    ADD COLUMN IF NOT EXISTS id_sede INT NULL,
    ADD COLUMN IF NOT EXISTS codigo_institucional_hash VARCHAR(255) NULL;

ALTER TABLE directorio_institucional
    ADD CONSTRAINT fk_directorio_sede
    FOREIGN KEY (id_sede) REFERENCES sedes(id)
    ON DELETE SET NULL;

CREATE INDEX idx_docentes_correo_institucional ON docentes(correo_institucional);
CREATE INDEX idx_directorio_correo_sede ON directorio_institucional(correo_institucional, id_sede, estado);
