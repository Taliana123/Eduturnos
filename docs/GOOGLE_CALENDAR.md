# Google Calendar institucional

## Estado y arquitectura

MySQL sigue siendo la fuente oficial de las citaciones. El formulario no espera a Google:
la creación de una cita y su tarea de sincronización se guardan en la misma transacción
local. Una tarea externa procesa la cola y usa la API oficial de Google Calendar. La cola
es idempotente por cita y calendario, guarda intentos, próximo intento y errores sin
credenciales y reintenta fallos temporales con espera exponencial. Los fallos permanentes
quedan visibles para administración.

El evento comparte solo el título genérico «Citación escolar», la fecha, hora y lugar. No
envía el nombre del estudiante, el motivo ni observaciones. La duración predeterminada es
30 minutos. Los avisos son notificaciones emergentes de Google Calendar a 24 horas y 2
horas; Google no garantiza correo ni SMS. La aplicación usa `America/Bogota`.

Los eventos se insertan con un identificador determinista. Si el evento ya existe, se
actualiza en vez de duplicarlo. Las cancelaciones de citas se envían como eliminaciones
idempotentes. Una reprogramación de EDUTURNOS crea la nueva cita y su tarea en la
transacción correspondiente.

## Antes de migrar o desplegar

1. Haz una copia de respaldo de la base de datos desde el administrador de alwaysdata o
   con `mysqldump` usando los datos de conexión del panel. No incluyas contraseñas en el
   comando, el historial del shell ni Git. Verifica la copia antes de continuar.
2. Conserva una copia segura de `SECRET_KEY`: los refresh tokens OAuth se cifran con esa
   clave y no se podrán descifrar si se cambia.
3. Despliega los archivos. En el siguiente arranque Flask, `database/bootstrap.py` aplica
   la migración aditiva `sql/google_calendar_sync.sql`. Esta crea la cola y añade el
   estado de cancelación y la fecha de prueba OAuth sin eliminar los registros existentes.
4. Comprueba en los logs que MySQL acepta la migración antes de habilitar la autorización.

## Configurar Google Cloud

1. Crea o selecciona un proyecto en Google Cloud Console y habilita **Google Calendar API**.
2. Configura la pantalla de consentimiento. Usa el tipo **Internal** solo si las cuentas
   institucionales pertenecen al mismo Google Workspace; de lo contrario usa **External**
   y añade las cuentas necesarias como usuarios de prueba. Google puede exigir verificación
   antes de autorizar usuarios fuera del conjunto de prueba.
3. Crea un cliente OAuth de tipo **Web application**.
4. Añade como origen autorizado:
   `https://eduturnos-jjfh.alwaysdata.net`
5. Añade como URI de redirección autorizada exactamente:
   `https://eduturnos-jjfh.alwaysdata.net/integraciones-google/callback`
6. Conserva el scope mínimo que solicita la aplicación:
   `openid`, `email` y `https://www.googleapis.com/auth/calendar.events`.
   Google puede someter el acceso a eventos a revisión; no intentes eludir esa revisión.
7. En el calendario institucional, concede permiso para modificar eventos a la cuenta que
   autorizará EDUTURNOS. Si el calendario está compartido, copia su **Calendar ID** desde la
   configuración del calendario. Si se trata de una cuenta institucional dedicada y su
   calendario principal es el destino, usa `primary`.
8. En EDUTURNOS, inicia sesión como Rector o Super Admin, abre **Mi cuenta → Calendarios
   conectados**, conecta la agenda institucional y acepta el consentimiento de Google. La
   aplicación verifica el acceso a la agenda antes de guardar la conexión.

El propietario debe crear el proyecto, aprobar el consentimiento y proporcionar el ID y
secreto del cliente OAuth. EDUTURNOS no puede hacer esas acciones en nombre del propietario.

## Variables de entorno

Configúralas en el panel de alwaysdata, nunca en el repositorio:

- `APP_ORIGIN=https://eduturnos-jjfh.alwaysdata.net`
- `GOOGLE_OAUTH_CLIENT_ID`: ID del cliente OAuth web.
- `GOOGLE_OAUTH_CLIENT_SECRET`: secreto del cliente OAuth web.
- `GOOGLE_CALENDAR_ID`: `primary` para el calendario principal de la cuenta autorizada o
  el ID del calendario institucional compartido.
- `SECRET_KEY`: clave estable de Flask, protegida y respaldada.

La ruta de retorno se construye a partir de `APP_ORIGIN` y de la ruta Flask
`/integraciones-google/callback`; ambos valores deben coincidir con Google Cloud. No guardes
credenciales OAuth, tokens ni copias de `.env` en Git.

## Programar la cola en alwaysdata

La aplicación está servida como Flask/WSGI mediante `wsgi.py`; la sincronización no depende
de un proceso web residente. En el panel de alwaysdata, verifica que la cuenta incluya la
ejecución de tareas programadas y crea una tarea cada cinco minutos:

```text
<ruta-del-entorno-python>/python <ruta-de-la-aplicacion>/tools/sincronizar_google_calendar.py
```

Configura el directorio de trabajo como la raíz del proyecto y asegúrate de que la tarea
herede las mismas variables de entorno y credenciales de MySQL que la aplicación WSGI. Las
rutas exactas dependen de la cuenta y del entorno Python configurado en el panel; no se
pueden deducir del repositorio. No mantengas un `while True` ni un worker persistente en
uWSGI. Revisa la salida/log de la tarea después de ejecutarla manualmente y de su primera
ejecución programada.

Si el plan o panel no permite tareas programadas, la cola persistirá, pero no se procesará
hasta que se configure un mecanismo permitido por alwaysdata. No declares la integración
operativa sin esa tarea.

## Comprobación y recuperación

- En **Calendarios conectados**, verifica el resultado y fecha de la prueba OAuth, el número
  de tareas pendientes y fallidas, la última sincronización correcta y el último error
  seguro.
- Para probar la ruta sin esperar al cron, ejecuta el comando anterior una vez desde el
  entorno Python de producción. La cuenta Google debe mostrar el evento genérico y sus dos
  avisos emergentes; EDUTURNOS debe mostrar una cola sin fallos.
- Si Google falla, no borres la cita ni la cola de MySQL. Corrige OAuth, permisos, ID del
  calendario o conectividad, vuelve a autorizar desde la cuenta administrativa si hace
  falta y reintenta la cita desde EDUTURNOS. Las tareas temporales reintentan
  automáticamente hasta el límite configurado.
- Si se produce un problema de despliegue, deshabilita la tarea programada sin borrar la
  base de datos. EDUTURNOS seguirá consultando y guardando citas; restaura los archivos de
  la versión anterior y reactiva el cron solo después de comprobar la conexión.
- Antes de restaurar MySQL, respalda también los datos actuales y valida el archivo de
  respaldo. No cambies `SECRET_KEY` mientras haya tokens OAuth que deban conservarse.

## Alcance de las pruebas

Las pruebas automatizadas locales cubren la creación transaccional de tareas, el
identificador idempotente, el formato privado del evento, los recordatorios, los reintentos
y el esquema aditivo. No simulan una respuesta exitosa de Google como prueba real. La
conexión efectiva, los permisos de la agenda compartida, la entrega de eventos y el cron de
alwaysdata requieren la autorización y verificación del propietario en el servidor.
