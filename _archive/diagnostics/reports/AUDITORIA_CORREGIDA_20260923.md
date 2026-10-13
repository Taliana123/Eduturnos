# Auditoría EDUTURNOS — 2026-09-23

## Correcciones aplicadas

- Se corrigió el arranque de `app.py`: el modo debug y el recargador ya no se fuerzan en producción.
- Se corrigió `tools/admin/probar_correo.py` para usar la firma actual del servicio de correo.
- `tools/enviar_recordatorios.py` quedó realmente independiente de Flask/Waitress: usa MySQL y SMTP directamente mediante `.env`.
- Los recordatorios internos 24 h / 2 h se mantienen como canal principal y el correo SMTP es adicional; un fallo de correo no cancela la notificación interna.
- Se añadió una ventana configurable mediante `REMINDER_WINDOW_MINUTES` (10 minutos por defecto).
- Se añadió migración compatible de los campos e índice de recordatorios en `database/bootstrap.py` para instalaciones existentes.
- Se corrigieron textos con codificación dañada en `routes/auth.py` y `routes/passwords.py`.
- Se eliminó el script de reparación de texto roto de `templates/solicitudes/index.html`, porque podía volver a insertar texto mojibake.
- Se actualizaron pruebas que correspondían a una versión anterior del servicio de correo/recordatorios.
- El paquete de distribución no contiene `.env`, entornos virtuales, `__pycache__`, `.pyc` ni copias de respaldo.

## Verificaciones realizadas

- Compilación sintáctica de los módulos Python principales: OK.
- Compilación sintáctica de pruebas: OK.
- `requirements.txt` contiene Flask, MySQL Connector, Waitress, python-dotenv, reportlab, openpyxl y Flask-Mail.
- FullCalendar está incluido localmente en `static/vendor/fullcalendar`, por lo que no depende de CDN.
- Las rutas principales están registradas en `app.py`.
- El esquema SQL incluye restricciones para evitar citas duplicadas por docente, estudiante y acudiente en la misma fecha/hora.
- El sistema tiene endpoints de salud (`/health/live`, `/health/ready`, `/health`) para diagnóstico y despliegue.

## Pendientes antes de producción

1. Ejecutar pruebas con MySQL real y con el entorno virtual del servidor.
2. Configurar `APP_ENV=production`, `SECRET_KEY` aleatoria, `APP_ORIGIN`, credenciales MySQL de producción y SMTP.
3. Publicar detrás de HTTPS y un servidor WSGI/proxy estable.
4. Configurar backups automáticos de MySQL y probar restauración.
5. Ejecutar pruebas extremo a extremo para registro, login por roles, citas, solicitudes, notificaciones, recuperación de contraseña y recordatorios.
6. Configurar el Programador de tareas de Windows para `tools/ejecutar_recordatorios.bat` o el equivalente del servidor.
7. Si una credencial SMTP real fue incluida accidentalmente en un paquete anterior, revocarla/rotarla antes de producción.
