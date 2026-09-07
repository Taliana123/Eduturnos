USE eduturnos;

-- ============================================
-- REPORTES SQL - EDUTURNOS
-- RESPONSABLE: DÍAZ
-- ============================================

-- CITACIONES POR ESTADO
SELECT
    e.nombre AS estado,
    COUNT(*) AS total
FROM citas c
INNER JOIN estados_cita e
    ON c.id_estado = e.id_estado
GROUP BY e.nombre;

-- CITACIONES POR FECHA
SELECT *
FROM citas
WHERE fecha BETWEEN '2026-09-01' AND '2026-09-30'
ORDER BY fecha, hora;

-- TOTAL DE CITACIONES
SELECT COUNT(*) AS total_citaciones
FROM citas;

-- INASISTENCIAS
SELECT COUNT(*) AS total_inasistencias
FROM citas c
INNER JOIN estados_cita e
    ON c.id_estado = e.id_estado
WHERE e.nombre = 'No asistió';