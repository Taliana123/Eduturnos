CREATE TABLE IF NOT EXISTS google_calendar_sync_queue (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT NOT NULL,
    scope_key VARCHAR(50) NOT NULL,
    google_event_id VARCHAR(100) NULL,
    operacion ENUM('upsert','delete') NOT NULL DEFAULT 'upsert',
    estado ENUM('Pendiente','Procesando','Reintentar','Fallido','Sincronizado') NOT NULL DEFAULT 'Pendiente',
    intentos SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    ultimo_intento DATETIME NULL,
    proximo_intento DATETIME NULL,
    ultimo_error VARCHAR(180) NULL,
    claim_token CHAR(36) NULL,
    lease_until DATETIME NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_google_queue_cita_scope (id_cita, scope_key),
    INDEX idx_google_queue_due (estado, proximo_intento, lease_until, id),
    INDEX idx_google_queue_scope_status (scope_key, estado, fecha_actualizacion)
) ENGINE=InnoDB;

ALTER TABLE integraciones_google
    ADD COLUMN fecha_prueba DATETIME NULL;

ALTER TABLE eventos_google
    MODIFY estado ENUM('Sincronizado','Fallido','Cancelado') NOT NULL DEFAULT 'Fallido';
