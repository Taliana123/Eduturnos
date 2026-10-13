# Recuperacion real por Gmail

EDUTURNOS envia un codigo de recuperacion de 6 digitos por SMTP.

## Configuracion
1. Activa la Verificacion en 2 pasos en la cuenta de Google que enviara los mensajes.
2. Crea una contrasena de aplicacion de Google para EDUTURNOS.
3. Ejecuta `tools/admin/configurar_correo_gmail.bat`.
4. Escribe el correo emisor y pega la contrasena de aplicacion cuando el asistente la solicite.
5. El asistente prueba `smtp.gmail.com:587` antes de guardar la configuracion.

No pongas tu contrasena normal de Google en `MAIL_PASSWORD`.

En produccion, guarda `.env` fuera del control de versiones y configura `PUBLIC_BASE_URL` con la URL HTTPS real.
