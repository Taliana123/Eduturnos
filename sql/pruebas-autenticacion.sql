USE eduturnos;

-- Usuarios registrados
SELECT
    id_usuario,
    documento,
    nombres,
    apellidos,
    correo,
    verificado,
    estado
FROM usuarios
ORDER BY id_usuario DESC;

-- Códigos de verificación
SELECT
    id_codigo,
    id_usuario,
    codigo,
    fecha_expiracion,
    utilizado
FROM codigos_verificacion
ORDER BY id_codigo DESC;

-- Acudientes vinculados
SELECT
    a.id_acudiente,
    a.id_usuario,
    a.documento,
    a.nombres,
    a.apellidos
FROM acudientes a
ORDER BY a.id_acudiente DESC;

-- Buscar documentos repetidos
SELECT
    documento,
    COUNT(*) AS cantidad
FROM usuarios
GROUP BY documento
HAVING COUNT(*) > 1;

-- Buscar correos repetidos
SELECT
    correo,
    COUNT(*) AS cantidad
FROM usuarios
WHERE correo IS NOT NULL
GROUP BY correo
HAVING COUNT(*) > 1;