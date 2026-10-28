# Puente gratuito con Google Calendar

EDUTURNOS puede publicar las citas en una única agenda institucional usando Google Apps Script. La persona dueña de esa agenda concede permiso una sola vez; el personal, acudientes y estudiantes no vinculan sus cuentas con EDUTURNOS. La cola existente guarda las operaciones y el servidor intenta publicarlas inmediatamente; el proceso programado sigue siendo necesario para reintentos.

El puente crea eventos genéricos (sin nombres ni observaciones), de 30 minutos, con avisos emergentes a 24 horas y 2 horas para la cuenta dueña de la agenda. Google trata los avisos de eventos como privados por usuario; compartir una agenda no copia esos avisos a todas las cuentas. Para que cada persona reciba el recordatorio en EDUTURNOS sin conectar una cuenta, usa también el proceso existente `tools/enviar_recordatorios.py`: crea notificaciones internas para participantes y envía correos si SMTP está configurado. Para recibir un aviso emergente de Google en el teléfono, cada usuario debe añadir la agenda compartida y configurar sus propias notificaciones; EDUTURNOS no puede activar remotamente las notificaciones de otros teléfonos.

## Preparar el proyecto de Apps Script

1. Inicia sesión en [script.google.com](https://script.google.com/) con la cuenta que será dueña de la agenda institucional y crea un proyecto.
2. Copia el contenido de `integrations/google_apps_script/EDUTURNOSCalendar.gs` en el archivo `.gs` del proyecto.
   Confirma que la agenda esté configurada con la zona horaria `America/Bogota`.
3. En **Configuración del proyecto → Propiedades del script**, crea estas propiedades:
   - `EDUTURNOS_WEBHOOK_SECRET`: una clave aleatoria de al menos 32 caracteres. Puedes generarla con Python: `python -c "import secrets; print(secrets.token_hex(32))"`.
   - `EDUTURNOS_CALENDAR_ID`: `primary` para la agenda principal de esa cuenta, o el ID de la agenda institucional compartida.
4. Selecciona `authorizeCalendarAccess` y pulsa **Ejecutar**. Revisa que la cuenta sea la correcta y autoriza acceso a Calendar. Esta es la única autorización de Google que necesita una persona administradora.
5. Pulsa **Implementar → Nueva implementación → Aplicación web**. Configura **Ejecutar como: yo** y acceso **Cualquier usuario** (acceso anónimo). Implementa y copia la URL terminada en `/exec`. No publiques el secreto en el código ni compartas esa URL públicamente.

Si la política de la cuenta de Google no permite implementar una aplicación web con acceso anónimo, este puente no podrá recibir solicitudes desde AlwaysData. En ese caso hay que usar el OAuth web existente o pedir al administrador de Google Workspace que permita el despliegue.

## Configurar AlwaysData

En las variables protegidas del sitio configura:

```text
GOOGLE_APPS_SCRIPT_URL=https://script.google.com/macros/s/ID_DE_IMPLEMENTACION/exec
GOOGLE_APPS_SCRIPT_SECRET=la_misma_clave_aleatoria_de_32_caracteres_o_mas
```

Pega exactamente el mismo secreto en Apps Script y AlwaysData. No hace falta llenar `GOOGLE_OAUTH_CLIENT_ID` ni `GOOGLE_OAUTH_CLIENT_SECRET` para este modo. Reinicia la aplicación después de actualizar las variables.

Luego, en EDUTURNOS, entra como Rector o Super Admin a **Mi cuenta → Calendarios conectados** y pulsa **Probar conexión**. La prueba debe confirmar que el script accede a la agenda. Al crear una cita, EDUTURNOS la pone en la cola transaccional y dispara un intento en segundo plano. Si Google o la red no responden, la tarea se reintenta con el proceso programado:

```text
<ruta-del-entorno-python>/python <ruta-de-la-aplicacion>/tools/sincronizar_google_calendar.py
```

Programa esa tarea cada cinco minutos en AlwaysData y comprueba en la pantalla de calendarios que los pendientes disminuyan y la sincronización aparezca correcta. Programa también `tools/enviar_recordatorios.py` cada cinco minutos si quieres notificaciones internas y correo 24 h/2 h a los participantes. Configura SMTP en AlwaysData para que se envíen correos; sin SMTP, se guardan las notificaciones dentro de EDUTURNOS. No elimines la cola si algo falla; el sistema conserva los reintentos.

## Alcance y límites

- El script opera solo con la agenda de la cuenta que lo implementa. El calendario debe pertenecer a esa cuenta o estar compartido con permiso para modificar eventos.
- Las citas llevan título genérico, fecha, hora, lugar y un identificador opaco para evitar duplicados. No se envían datos del estudiante o acudiente.
- El puente autentica las llamadas del servidor con HMAC, ventana de tiempo limitada y protección contra repetición. Guarda el secreto solo en propiedades privadas de Apps Script y en las variables protegidas del servidor.
- Apps Script tiene cuotas diarias gratuitas, actualmente hasta 5.000 eventos creados por día en cuentas de consumidor y 10.000 en Google Workspace. Google puede cambiar esas cuotas; consulta [los límites vigentes](https://developers.google.com/apps-script/guides/services/quotas).
- Los avisos emergentes configurados en el evento aplican a la cuenta dueña; Google no comparte las preferencias personales de recordatorio con otros usuarios. Los usuarios reciben avisos internos de EDUTURNOS mediante el proceso de recordatorios, y correo cuando SMTP está disponible. El teléfono puede mostrar notificaciones emergentes de Google si cada persona añade la agenda y configura sus alertas.
- Google Apps Script y Google Calendar no garantizan entrega fuera de sus límites o con las notificaciones del teléfono desactivadas. EDUTURNOS sigue siendo la fuente oficial de las citas.
