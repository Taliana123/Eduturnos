USE eduturnos;

-- ============================================
-- PRUEBAS DE AUTENTICACIÓN - EDUTURNOS
-- RESPONSABLE: SANDY
-- ============================================

-- 1. REGISTRO CORRECTO
-- Se registra un usuario con datos únicos.
INSERT INTO usuarios (
    id_rol,
    tipo_documento,
    documento,
    nombres,
    apellidos,
    correo,
    contrasena,
    estado
)
VALUES (
    1,
    'CC',
    '1000000001',
    'Usuario',
    'Prueba',
    'usuario.prueba@eduturnos.com',
    'contraseña_hash_prueba',
    'Pendiente'
);

SELECT * FROM usuarios
WHERE documento = '1000000001';


-- 2. DOCUMENTO DUPLICADO
-- Debe generar un error porque el documento es UNIQUE.
INSERT INTO usuarios (
    id_rol,
    tipo_documento,
    documento,
    nombres,
    apellidos,
    correo,
    contrasena,
    estado
)
VALUES (
    1,
    'CC',
    '1000000001',
    'Otro',
    'Usuario',
    'otro.usuario@eduturnos.com',
    'contraseña_hash_prueba',
    'Pendiente'
);


-- 3. CORREO DUPLICADO
-- Debe generar un error porque el correo es UNIQUE.
INSERT INTO usuarios (
    id_rol,
    tipo_documento,
    documento,
    nombres,
    apellidos,
    correo,
    contrasena,
    estado
)
VALUES (
    1,
    'CC',
    '1000000002',
    'Segundo',
    'Usuario',
    'usuario.prueba@eduturnos.com',
    'contraseña_hash_prueba',
    'Pendiente'
);


-- 4. VERIFICACIÓN CORRECTA
-- Crear un código de prueba para el usuario.
INSERT INTO codigos_verificacion (
    id_usuario,
    codigo,
    utilizado
)
VALUES (
    1,
    '123456',
    FALSE
);

SELECT *
FROM codigos_verificacion
WHERE codigo = '123456';


-- 5. CÓDIGO INCORRECTO
-- Consulta utilizando un código diferente al registrado.
SELECT *
FROM codigos_verificacion
WHERE id_usuario = 1
AND codigo = '999999'
AND utilizado = FALSE;


-- 6. LOGIN CORRECTO
-- Consulta de un usuario activo.
SELECT id_usuario, id_rol, nombres, apellidos, correo, estado
FROM usuarios
WHERE documento = '1000000001'
AND estado = 'Activo';


-- 7. CONTRASEÑA INCORRECTA
-- La validación de la contraseña se realiza en PHP.
-- Esta consulta permite comprobar que el usuario existe.
SELECT id_usuario, contrasena, estado
FROM usuarios
WHERE documento = '1000000001';


-- 8. USUARIO INEXISTENTE
-- Debe retornar cero registros.
SELECT *
FROM usuarios
WHERE documento = '9999999999';


-- 9. USUARIO INACTIVO
-- Cambiar temporalmente el estado para realizar la prueba.
UPDATE usuarios
SET estado = 'Inactivo'
WHERE documento = '1000000001';

SELECT *
FROM usuarios
WHERE documento = '1000000001'
AND estado = 'Activo';


-- 10. CIERRE DE SESIÓN
-- La finalización de la sesión se controla mediante PHP.
-- Esta consulta permite comprobar el usuario utilizado en la prueba.
SELECT id_usuario, nombres, estado
FROM usuarios
WHERE documento = '1000000001';