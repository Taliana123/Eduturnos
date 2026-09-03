USE eduturnos;

-- ============================================
-- DATOS DE PRUEBA - SANDY
-- ============================================

-- 1. Institución
INSERT INTO instituciones (nombre, nit)
VALUES
('Institución Educativa José Joaquín Flórez Hernández', '900000000-0');

-- 2. Sedes
INSERT INTO sedes (id_institucion, nombre)
VALUES
(1, 'Sede Principal'),
(1, 'Picaleña'),
(1, 'Bello Horizonte');

-- 3. Jornadas
INSERT INTO jornadas (nombre)
VALUES
('Mañana'),
('Tarde'),
('Nocturna');

-- 4. Grupos de grado 10
INSERT INTO grupos (id_grado, nombre)
VALUES
(10, '10-1'),
(10, '10-2'),
(10, '10-3'),
(10, '10-4'),
(10, '10-5'),
(10, '10-6');

-- ============================================
-- CONSULTAS DE VERIFICACIÓN
-- ============================================

SELECT * FROM instituciones;

SELECT * FROM sedes;

SELECT * FROM jornadas;

SELECT * FROM grados;

SELECT * FROM grupos;

SELECT * FROM roles;

SELECT * FROM estados_cita;

SELECT * FROM motivos;

-- ============================================
-- VERIFICAR GRUPOS DEL GRADO 10
-- ============================================

SELECT
    g.id_grupo,
    gr.nombre AS grado,
    g.nombre AS grupo
FROM grupos g
INNER JOIN grados gr
    ON g.id_grado = gr.id_grado
WHERE gr.nombre = '10°';

-- ============================================
-- VERIFICAR DUPLICADOS
-- ============================================

SELECT documento
FROM usuarios
GROUP BY documento
HAVING COUNT(*) > 1;

SELECT codigo_estudiante
FROM estudiantes
GROUP BY codigo_estudiante
HAVING COUNT(*) > 1;