# Arquitectura de EDUTURNOS

## Capas

1. **Presentación:** Flask + Jinja + CSS responsive + JavaScript mínimo.
2. **Aplicación:** Blueprints por dominio: autenticación, citas, citaciones, seguimiento, calendario, notificaciones, justificaciones, estudiantes, acudientes, docentes, reportes y configuración.
3. **Persistencia:** MySQL 8.x/InnoDB con claves foráneas, índices y restricciones anti-duplicado.
4. **Despliegue:** Waitress detrás de un proxy TLS (Caddy/Nginx) o contenedor en un proveedor cloud.

## Seguridad

- Rol efectivo consultado desde MySQL; el navegador no decide privilegios.
- CSRF en métodos mutables.
- Contraseñas con hash lento de Werkzeug.
- Rotación de sesión por autenticación y expiración por inactividad.
- Cookies HttpOnly/SameSite y `Secure` en producción.
- Cabeceras CSP, HSTS (HTTPS), frame-ancestors y Permissions-Policy.
- Bloqueo por intentos fallidos.
- Tokens de recuperación aleatorios almacenados como SHA-256.
- Consultas parametrizadas.
- Auditoría de acciones críticas.
- Límites de tamaño de solicitud.

## Flujo de datos

`Usuario -> HTTPS -> Proxy -> Waitress -> Flask -> MySQL`

El navegador nunca se conecta directamente a MySQL.
