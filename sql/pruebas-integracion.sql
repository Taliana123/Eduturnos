USE eduturnos;

-- ============================================
-- PRUEBAS FINALES DE INTEGRACIÓN - EDUTURNOS
-- RESPONSABLE: SANDY
-- ============================================

-- ============================================
-- 1. AUTENTICACIÓN
-- ============================================

-- Registro
SELECT *
FROM usuarios;

-- Verificación
SELECT *
FROM codigos_verificacion;

-- Login
SELECT id_usuario, id_rol, nombres, apellidos, correo, estado
FROM usuarios
WHERE estado = 'Activo';

-- Dashboard
SELECT id_usuario, id_rol, nombres, apellidos
FROM usuarios
WHERE estado = 'Activo';


-- ============================================
-- 2. CITACIONES
-- ============================================

-- Crear / consultar
SELECT *
FROM citas;

-- Modificar
SELECT id_cita, fecha, hora, lugar, observaciones
FROM citas;

-- Confirmar
SELECT c.id_cita, e.nombre AS estado
FROM citas c
INNER JOIN estados_cita e
    ON c.id_estado = e.id_estado
WHERE e.nombre = 'Confirmada';

-- Reprogramar
SELECT id_cita, fecha, hora
FROM citas
ORDER BY fecha, hora;

-- Cancelar
SELECT c.id_cita, e.nombre AS estado
FROM citas c
INNER JOIN estados_cita e
    ON c.id_estado = e.id_estado
WHERE e.nombre = 'Cancelada';


-- ============================================
-- 3. SEGUIMIENTO
-- ============================================

-- Citación
SELECT *
FROM citas;

-- Estado
SELECT c.id_cita, e.nombre AS estado
FROM citas c
INNER JOIN estados_cita e
    ON c.id_estado = e.id_estado;

-- Notificación
SELECT *
FROM notificaciones;

-- Historial
SELECT *
FROM seguimiento_citas
ORDER BY fecha DESC;


-- ============================================
-- 4. REPORTES
-- ============================================

-- Base de datos / consulta
SELECT *
FROM citas;

-- Filtro por estado
SELECT c.id_cita, c.fecha, c.hora, e.nombre AS estado
FROM citas c
INNER JOIN estados_cita e
    ON c.id_estado = e.id_estado
WHERE e.nombre = 'Confirmada';

-- Filtro por fecha
SELECT *
FROM citas
WHERE fecha BETWEEN '2026-09-01' AND '2026-09-30'
ORDER BY fecha, hora;

-- Resultado
SELECT COUNT(*) AS total_citaciones
FROM citas;