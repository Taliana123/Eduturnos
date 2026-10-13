# Guía de producción

## Ruta recomendada
1. Servidor Linux o servicio cloud con Docker.
2. Copiar el proyecto.
3. Crear `.env` a partir de `.env.example`.
4. Definir secretos fuertes y el dominio real.
5. Ejecutar `docker compose -f docker-compose.prod.yml up -d --build`.
6. Confirmar `https://DOMINIO/health`.
7. Configurar backups externos.
8. Cargar el directorio institucional real.
9. Ejecutar las pruebas de staging.

## Variables críticas
- `SECRET_KEY`
- `DOMAIN`
- `MYSQL_ROOT_PASSWORD`
- `MYSQL_PASSWORD`
- `APP_ORIGIN`
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` si se usa correo

## Importante
El dominio, DNS, servidor, correo SMTP y los certificados no pueden estar contenidos físicamente
como parte del ZIP. El proyecto deja la configuración preparada, pero esos recursos deben ser
contratados/configurados fuera de la aplicación.
