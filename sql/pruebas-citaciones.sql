USE eduturnos;

-- ============================================
-- PRUEBAS DEL MÓDULO DE CITACIONES - EDUTURNOS
-- RESPONSABLE: SANDY
-- ============================================

-- 1. CREAR CITACIÓN
INSERT INTO citas (
    id_estudiante,
    id_acudiente,
    id_docente,
    id_motivo,
    id_estado,
    fecha,
    hora,
    lugar,
    observaciones
)
VALUES (
    1,
    1,
    1,
    1,
    1,
    '2026-09-15',
    '08:00:00',
    'Sala de reuniones',
    'Citación de prueba'
);

SELECT *
FROM citas
WHERE id_estudiante = 1
AND fecha = '2026-09-15'
AND hora = '08:00:00';


-- 2. CAMPOS VACÍOS
INSERT INTO citas (
    id_estudiante,
    id_acudiente,
    id_docente,
    id_motivo,
    id_estado,
    fecha,
    hora,
    lugar,
    observaciones
)
VALUES (
    1,
    1,
    1,
    1,
    1,
    NULL,
    NULL,
    NULL,
    'Prueba de campos vacíos'
);


-- 3. FECHA INVÁLIDA
INSERT INTO citas (
    id_estudiante,
    id_acudiente,
    id_docente,
    id_motivo,
    id_estado,
    fecha,
    hora,
    lugar,
    observaciones
)
VALUES (
    1,
    1,
    1,
    1,
    1,
    '2026-02-30',
    '09:00:00',
    'Sala de reuniones',
    'Prueba de fecha inválida'
);


-- 4. HORARIO OCUPADO
INSERT INTO citas (
    id_estudiante,
    id_acudiente,
    id_docente,
    id_motivo,
    id_estado,
    fecha,
    hora,
    lugar,
    observaciones
)
VALUES (
    1,
    1,
    1,
    1,
    1,
    '2026-09-15',
    '08:00:00',
    'Sala de reuniones',
    'Prueba de horario ocupado'
);


-- 5. EDITAR CITACIÓN
UPDATE citas
SET fecha = '2026-09-16',
    hora = '10:00:00',
    lugar = 'Aula 10',
    observaciones = 'Citación modificada'
WHERE id_cita = 1;

SELECT *
FROM citas
WHERE id_cita = 1;


-- 6. CANCELAR CITACIÓN
UPDATE citas
SET id_estado = (
    SELECT id_estado
    FROM estados_cita
    WHERE nombre = 'Cancelada'
    LIMIT 1
)
WHERE id_cita = 1;

SELECT *
FROM citas
WHERE id_cita = 1;


-- 7. CONSULTAR CITACIONES
SELECT
    c.id_cita,
    c.fecha,
    c.hora,
    c.lugar,
    e.nombres AS estudiante,
    a.nombres AS acudiente,
    m.nombre AS motivo,
    ec.nombre AS estado
FROM citas c
INNER JOIN estudiantes e
    ON c.id_estudiante = e.id_estudiante
INNER JOIN acudientes a
    ON c.id_acudiente = a.id_acudiente
INNER JOIN motivos m
    ON c.id_motivo = m.id_motivo
INNER JOIN estados_cita ec
    ON c.id_estado = ec.id_estado
ORDER BY c.fecha DESC, c.hora DESC;

SELECT * FROM estudiantes;
SELECT * FROM acudientes;
SELECT * FROM docentes;
SELECT * FROM motivos;
SELECT * FROM estados_cita;