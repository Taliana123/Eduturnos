USE eduturnos;

-- =========================================================
-- CAMBIOS DE AUTENTICACIÓN EDUTURNOS
-- =========================================================

-- Agregar tipo de documento al usuario
ALTER TABLE usuarios
ADD COLUMN tipo_documento VARCHAR(20) NULL AFTER id_rol;

-- Relacionar acudiente con su usuario de acceso
ALTER TABLE acudientes
ADD COLUMN id_usuario INT NULL UNIQUE AFTER id_acudiente;

ALTER TABLE acudientes
ADD CONSTRAINT fk_acudiente_usuario
FOREIGN KEY (id_usuario)
REFERENCES usuarios(id_usuario)
ON DELETE SET NULL
ON UPDATE CASCADE;

-- Índices para mejorar consultas
CREATE INDEX idx_citas_fecha_hora
ON citas(fecha, hora);

CREATE INDEX idx_citas_estudiante
ON citas(id_estudiante);

CREATE INDEX idx_citas_docente
ON citas(id_docente);

CREATE INDEX idx_citas_acudiente
ON citas(id_acudiente);

CREATE INDEX idx_notificaciones_usuario
ON notificaciones(id_usuario);

CREATE INDEX idx_seguimiento_cita
ON seguimiento_citas(id_cita);

CREATE INDEX idx_codigos_usuario
ON codigos_verificacion(id_usuario);

-- Evitar códigos de verificación repetidos activos
CREATE INDEX idx_codigo_verificacion
ON codigos_verificacion(id_usuario, codigo, utilizado);