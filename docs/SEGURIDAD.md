# Seguridad de EDUTURNOS

EDUTURNOS se organiza tomando como referencia OWASP ASVS 5.0 en autenticación, sesiones, autorización, validación, protección de datos, comunicación, configuración y registro de seguridad. La meta del proyecto es cubrir un nivel de aplicación institucional; antes de exposición pública debe realizarse una revisión independiente/pentest. [OWASP ASVS](https://owasp.org/projects/asvs)

## Controles implementados

- Hash de contraseñas con el mecanismo seguro de Werkzeug.
- Política mínima de contraseña de 12 caracteres con diversidad de caracteres.
- CSRF en operaciones mutables.
- Cookies HttpOnly y SameSite; `Secure` en producción.
- CSP, HSTS en HTTPS, X-Frame-Options, nosniff, Referrer-Policy y Permissions-Policy.
- Sesión asociada a un usuario del servidor, con expiración.
- Bloqueo por cuenta y límite adicional por identificador + IP.
- Tokens de recuperación aleatorios y almacenados como hash SHA-256.
- SQL parametrizado.
- Separación de datos por rol y validación de propiedad de las citas.
- Auditoría de acciones críticas.
- No se distribuyen códigos institucionales reales en el repositorio.

## Pendientes obligatorios antes de producción

- Secretos reales en el gestor de secretos/variables del hosting.
- HTTPS y DNS correctamente configurados.
- SMTP seguro para recuperación de contraseña.
- Backups cifrados y prueba de restauración.
- Revisión de logs y alertas.
- Pruebas de carga y revisión de autorización con cuentas reales.
- Pentest/revisión de seguridad antes de anunciar el lanzamiento.
