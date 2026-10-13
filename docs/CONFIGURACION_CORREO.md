# Configuración de correo de EDUTURNOS

EDUTURNOS tiene una sola cuenta remitente del sistema. Los destinatarios pueden ser cuentas Gmail personales, Google Workspace u otros proveedores; cada usuario solo registra su propio correo en EDUTURNOS.

## En el servidor

Configura estas variables mediante `.env` o el asistente `tools/admin/configurar_correo.bat`: `MAIL_MODE=smtp`, `MAIL_HOST`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`, `MAIL_USE_TLS` y, si aplica, `MAIL_USE_SSL`.

## Gmail

Cuando la cuenta remitente es Google, utiliza el mecanismo de autenticación permitido por esa cuenta. Una contraseña de aplicación solo es posible cuando Google la habilita para esa cuenta; una organización de Google Workspace puede restringirla.

Nunca pongas la contraseña de la cuenta ni secretos de SMTP en formularios públicos, código fuente o GitHub.

## Usuarios destinatarios

No necesitan configurar nada de correo. El sistema envía automáticamente al correo registrado de la cuenta que solicita la recuperación o recibe una notificación.
