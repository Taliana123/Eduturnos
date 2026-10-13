# Checklist de lanzamiento EDUTURNOS

## Código
- Backend y frontend integrados.
- MySQL central.
- Roles y permisos verificados en backend.
- CSRF, sesiones seguras y contraseñas con hash.
- Recuperación de contraseña con código de un solo uso y vencimiento.
- Solicitudes, citas, calendario, notificaciones, seguimiento, justificaciones y auditoría.
- Importación CSV/XLSX y reportes CSV/XLSX/PDF.
- Recordatorios independientes de 24 h y 2 h.

## Infraestructura
- Servidor de aplicación.
- MySQL central.
- Dominio.
- DNS.
- HTTPS.
- SMTP del sistema.
- Backups y prueba de restauración.
- Datos institucionales reales cargados de forma segura.

## Antes de publicar
1. Ejecutar las pruebas desde una copia limpia.
2. Probar los cinco roles y las rutas administrativas por URL directa.
3. Probar recuperación con un correo real de prueba.
4. Verificar que no existan secretos en el repositorio.
5. Activar `APP_ENV=production` y una `SECRET_KEY` aleatoria.
6. Registrar la tarea de recordatorios fuera de Flask.
