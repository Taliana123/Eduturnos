USE eduturnos;

-- =========================================================
-- SEGUIMIENTO Y NOTIFICACIONES
-- Compatible con la estructura actual
-- =========================================================

SELECT *
FROM seguimiento_citas
ORDER BY fecha DESC;

SELECT *
FROM notificaciones
ORDER BY fecha_envio DESC;