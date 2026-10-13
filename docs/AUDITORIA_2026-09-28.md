# Auditoría integral EDUTURNOS — 2026-09-28

## Estado
El código fuente fue unificado a un único proyecto y un único esquema MySQL.

## Corregido
- Registro de los 11 blueprints en `app.py`.
- Esquema único `database/eduturnos.sql` y copia operativa en `sql/eduturnos.sql`.
- Claves principales coherentes (`id`) y claves foráneas (`id_usuario`, `id_estudiante`, etc.) donde corresponden.
- Campos de seguridad de usuarios.
- Directorio institucional para Rector y Coordinación.
- Código institucional de docentes.
- Calendario, reportes, notificaciones, citas y autenticación alineados al esquema.
- Recuperación de contraseña con código de 6 dígitos, sin código en la URL.
- El cierre de periodo conserva el historial de citas.
- Eliminadas copias anidadas, `venv`, cachés y archivos compilados del paquete.
- Utilidades antiguas movidas a `tools/`.
- Documentación consolidada.

## Pruebas realizadas
- Compilación de todos los `.py`: OK.
- Revisión de endpoints referenciados por plantillas: sin referencias sin ruta.
- Búsqueda de `IN ()`: sin resultados.
- Búsqueda de columnas antiguas de usuario: sin resultados en el código principal.
- Búsqueda de mojibake `Ã`, `Â`, `â†` y `undefined`: sin resultados en plantillas/código principal.

## Pendiente de ejecutar en Windows
La prueba real de MySQL/HTTP requiere las dependencias y el servidor MySQL del equipo del proyecto. Ejecutar `setup_database.py`, `test_db.py` y `pytest -q`.

## Pantallas protegidas visualmente
No se rediseñó Inicio, Iniciar sesión ni Crear cuenta. La recuperación se implementó usando el mismo lenguaje visual existente porque en esta copia no había un flujo funcional completo.
