# Despliegue de EDUTURNOS

## Opción 1: servidor propio con Docker

Usa `docker-compose.prod.yml` y `.env`. Define `DOMAIN`, `SECRET_KEY`, credenciales MySQL y SMTP. Caddy gestiona HTTPS para el dominio apuntado por DNS.

Para las integraciones opcionales consulta [INTEGRACIONES.md](INTEGRACIONES.md). Google Calendar requiere un cliente OAuth web, consent screen, callback HTTPS y `GOOGLE_OAUTH_CLIENT_ID`/`GOOGLE_OAUTH_CLIENT_SECRET`. EDUBOT responde preguntas frecuentes localmente y usa Groq para preguntas abiertas; configura `GROQ_API_KEY` únicamente en las variables de entorno protegidas del servidor, nunca en el repositorio ni en el navegador. Consulta [INTEGRACIONES.md](INTEGRACIONES.md) para sus límites de privacidad y cuota.

## Opción 2: proveedor cloud

Sube el repositorio a un proveedor que ejecute Docker o Waitress y usa MySQL gestionado. Configura las mismas variables de entorno. No publiques las credenciales en Git.

## Verificación

- `/health` debe responder HTTP 200 y `database=ok`.
- `DEV_MODE=0`.
- `APP_ENV=production`.
- `SESSION_COOKIE_SECURE=1`.
- La URL pública usa HTTPS.
- Se restauró una copia de seguridad de MySQL antes de declarar el lanzamiento.
