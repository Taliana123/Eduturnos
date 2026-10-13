# Correo de recuperación de EDUTURNOS

EDUTURNOS usa las bibliotecas estándar de Python `smtplib` y `email` para enviar el correo. Por eso no hace falta instalar otra biblioteca SMTP.

La arquitectura es multiusuario: el servidor tiene **una sola cuenta remitente**. Cada usuario únicamente registra su propio correo; al recuperar acceso, EDUTURNOS envía el código a ese destinatario.

## Configuración única

1. Ejecuta `tools/admin/configurar_correo.bat` una sola vez en el equipo/servidor que ejecuta EDUTURNOS.
2. Escribe el correo que será el remitente del sistema.
3. Escribe la contraseña de aplicación de Google si ese remitente es Gmail/Google y esa cuenta usa contraseña de aplicación.
4. El asistente guarda la configuración en `.env`, que está excluido del control de versiones.
5. Ejecuta `tools/admin/probar_correo.bat` para verificar el envío real.

## Gmail

SMTP recomendado para Gmail: `smtp.gmail.com` con STARTTLS en el puerto `587`; también se puede usar SSL en `465`.

La contraseña de aplicación debe ser la credencial específica del remitente, nunca la contraseña normal de Google.

## Producción

Configura la cuenta remitente únicamente en el servidor. Los destinatarios pueden ser cuentas Gmail, institucionales o de otros proveedores. `PUBLIC_BASE_URL`/`APP_ORIGIN` debe usar la URL pública HTTPS del sitio.
