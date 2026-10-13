# Recordatorios EDUTURNOS

EDUTURNOS ejecuta los recordatorios en un proceso independiente. Flask y Waitress no crean hilos ni schedulers para esta función.

## Qué hace

El script `tools/enviar_recordatorios.py` consulta MySQL y procesa citas en estado `Pendiente` o `Confirmada`:

- 24 horas antes.
- 2 horas antes.

Los campos de control son `citas.recordatorio_24h_enviado` y `citas.recordatorio_2h_enviado`. La marca y las notificaciones internas se guardan dentro de una transacción con bloqueo de la cita, evitando que dos ejecuciones concurrentes creen el mismo recordatorio.

El correo SMTP es un canal adicional. Si SMTP no está configurado o falla, la notificación interna no se pierde y el proceso registra el error sin detener Flask.

## Ejecución manual

Desde la carpeta del proyecto:

```powershell
python tools/enviar_recordatorios.py
```

En Windows, cuando el entorno virtual ya exista:

```powershell
.\venv\Scripts\python.exe tools\enviar_recordatorios.py
```

## Programación recomendada en Windows

Ejecuta una vez:

```text
tools\INSTALAR_RECORDATORIOS.bat
```

Esto registra una única tarea de Windows llamada `EDUTURNOS - Recordatorios` con frecuencia de 5 minutos. Para retirarla usa `tools\ELIMINAR_RECORDATORIOS.bat`.

## Linux / cron

También puede programarse el mismo script desde cron. Ejemplo cada 5 minutos:

```cron
*/5 * * * * cd /ruta/EDUTURNOS && /ruta/EDUTURNOS/venv/bin/python tools/enviar_recordatorios.py
```

## Variables SMTP

Usa la configuración existente de `.env`/entorno: `MAIL_MODE=smtp`, `MAIL_HOST`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`, `MAIL_USE_TLS`, `MAIL_USE_SSL` y `MAIL_TIMEOUT`.

No escribas credenciales en los scripts ni en los logs.
