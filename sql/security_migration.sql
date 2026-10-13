USE eduturnos;

ALTER TABLE usuarios
    ADD COLUMN intentos_fallidos INT NOT NULL DEFAULT 0,
    ADD COLUMN bloqueado_hasta DATETIME NULL,
    ADD COLUMN ultimo_acceso DATETIME NULL;
