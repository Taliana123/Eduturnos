USE eduturnos;

-- =========================================================
-- PRUEBAS DE INTEGRIDAD EDUTURNOS
-- =========================================================

-- 1. Verificar roles
SELECT *
FROM roles;

-- 2. Verificar usuarios
SELECT
    id_usuario,
    documento,
    nombres,
    apellidos,
    correo,
    verificado,
    estado
FROM usuarios;

-- 3. Verificar acudientes relacionados
SELECT
    a.id_acudiente,
    a.documento,
    a.nombres,
    a.apellidos,
    a.id_usuario
FROM acudientes a;

-- 4. Verificar estudiantes y acudientes
SELECT
    e.codigo_estudiantil,
    CONCAT(e.nombres, ' ', e.apellidos) AS estudiante,
    CONCAT(a.nombres, ' ', a.apellidos) AS acudiente
FROM estudiante_acudiente ea
INNER JOIN estudiantes e
    ON ea.id_estudiante = e.id_estudiante
INNER JOIN acudientes a
    ON ea.id_acudiente = a.id_acudiente;

-- 5. Verificar docentes
SELECT
    d.id_docente,
    u.documento,
    CONCAT(u.nombres, ' ', u.apellidos) AS docente
FROM docentes d
INNER JOIN usuarios u
    ON d.id_usuario = u.id_usuario;

-- 6. Verificar citas
SELECT
    c.id_cita,
    c.fecha,
    c.hora,
    ec.nombre AS estado
FROM citas c
INNER JOIN estados_cita ec
    ON c.id_estado = ec.id_estado
ORDER BY c.fecha DESC;

-- 7. Verificar seguimiento
SELECT *
FROM seguimiento_citas
ORDER BY fecha DESC;

-- 8. Verificar notificaciones
SELECT *
FROM notificaciones
ORDER BY fecha_envio DESC;

-- 9. Verificar auditoría
SELECT *
FROM auditoria
ORDER BY fecha DESC;

-- 10. Verificar citas duplicadas
SELECT
    fecha,
    hora,
    id_docente,
    COUNT(*) AS cantidad
FROM citas
GROUP BY
    fecha,
    hora,
    id_docente
HAVING COUNT(*) > 1;