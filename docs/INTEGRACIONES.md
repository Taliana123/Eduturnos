# Integraciones opcionales

## Google Calendar

EDUTURNOS conserva el calendario interno como fuente principal. Después de confirmar el guardado local, intenta copiar un evento genérico a la agenda institucional y/o al calendario personal conectado. Los detalles de estudiantes, acudientes y observaciones no se envían a Google. Si Google falla, la cita local se conserva y el evento se puede reintentar desde la cita.

Para activar OAuth se necesita:

1. Publicar EDUTURNOS detrás de HTTPS en un dominio estable. La dirección LAN `http://192.168.18.24:5000` no puede recibir el callback OAuth de Google.
2. Crear un proyecto en Google Cloud, habilitar Google Calendar API y configurar la pantalla de consentimiento.
3. Crear credenciales OAuth de tipo aplicación web. Registrar como URI autorizada de retorno exactamente el valor mostrado en **Mi cuenta > Calendarios conectados**.
4. Configurar `APP_ORIGIN=https://tu-dominio` sin barra final, `GOOGLE_OAUTH_CLIENT_ID` y `GOOGLE_OAUTH_CLIENT_SECRET` en `.env` o en los secretos del servidor.
5. Aplicar `sql/school_workflow.sql` mediante el arranque/migración de EDUTURNOS y reiniciar la app.
6. El Rector o Super Admin conecta el calendario institucional; cada Docente, Rector o Administrador/Coordinador conecta opcionalmente su propio calendario.

Los refresh tokens se cifran usando `SECRET_KEY`; mantener una SECRET_KEY estable y un backup protegido es necesario para conservar las conexiones. Si se cambia esa clave, habrá que volver a autorizar Google. Google puede exigir verificación OAuth y limitar aplicaciones externas en modo prueba.

### Publicación para cualquier cuenta Google

El modo de prueba de una app externa solo permite autorizar las cuentas añadidas como usuarios de prueba. Para solicitar producción abierta, primero publica EDUTURNOS en un dominio HTTPS estable que controle la institución, verifica ese dominio en Google Search Console y completa en Google Auth Platform los enlaces públicos de página principal, Política de Privacidad y Condiciones del Servicio. La portada debe describir EDUTURNOS e incluir el enlace a privacidad; las páginas legales deben estar bajo el mismo dominio autorizado.

El scope `https://www.googleapis.com/auth/calendar.events` puede requerir verificación de acceso a datos sensibles. Google puede pedir una explicación de por qué se necesita ese scope, una demostración en video del flujo OAuth y revisión de marca. Cambiar el estado a producción por sí solo no sustituye la revisión ni garantiza aprobación. Las rutas públicas preparadas son `/privacidad` y `/terminos`; el contenido debe ser revisado y aprobado por la institución antes de enviarlo a Google.

## Ayuda con Gemini

Con `BEEPY_ENABLED=1`, Ayuda usa Beepy y no requiere una clave Gemini. Para volver al chat Gemini, configura `BEEPY_ENABLED=0` y reinicia el servidor.

El chat es solo para Super Admin, Rector, Coordinación y Docentes. Es una ayuda general, no consulta datos de EDUTURNOS y no debe recibir información personal o expedientes de estudiantes. No conserva conversaciones en la base de datos. Al activarlo, cada pregunta se envía a Google Gemini.

Configura `GEMINI_API_KEY` y, opcionalmente, `GEMINI_MODEL` en `.env` o en los secretos del servidor. La API puede tener nivel gratuito, límites o cambios de facturación según el proyecto, región y modelo; revisa las condiciones y cuota vigentes en Google AI Studio. La app responde con un aviso si no está configurada y mantiene el dashboard operativo.

## Ayuda con Beepy

- `BEEPY_ENABLED=1` activa la integración y `BEEPY_DOMAIN` identifica el dominio registrado en Beepy. Por defecto es `seventy-excavator-designate.ngrok-free.dev`.
- Inicio carga el script únicamente desde ese dominio público. La dirección LAN no carga el widget público para evitar registrar un dominio incorrecto.
- Ayuda aparece para todos los roles autenticados. Al desplegarla carga `/asistente/beepy`, que redirige al enlace oficial de la invitación configurado en `BEEPY_CHAT_URL`, dentro de un iframe externo. Por defecto usa `https://www.beepychatbot.com/u/1nLBFlV/`. Beepy inicia su propio guion y gestiona la conversación; EduTurnos no envía cookies, nombres ni expedientes al proveedor. El iframe usa `referrerpolicy="no-referrer"`.
- Los módulos privados no cargan `eye.js`: el script externo queda fuera de la página que contiene sus datos. Los mensajes escritos voluntariamente en el chat sí se envían a Beepy. No incluir información personal de estudiantes y revisar las condiciones de privacidad del proveedor.
- El widget de Inicio usa `cid=27952`, `iidf=21859` y `lang=es`. El enlace compartido de Ayuda se obtiene desde Live chat > Invitaciones > Link para compartir. Solo se aceptan enlaces HTTPS de `www.beepychatbot.com/u/`; no se utilizan URLs internas de conversación ni URLs de vista previa.
- Nombre del bot, saludo inicial, colores y respuestas se administran en Beepy. Cambiar el nombre mediante una conversación no modifica el saludo inicial de forma permanente.
- La política CSP autoriza scripts del proveedor solo en Inicio; permite su iframe en Ayuda, sus imágenes y sonido en Inicio y no habilita `unsafe-inline` ni `unsafe-eval` para scripts.
- Si cambia el dominio público o la cuenta de Beepy, revisar los identificadores, actualizar `BEEPY_DOMAIN` y reiniciar EduTurnos. El túnel ngrok y EduTurnos deben seguir encendidos.

## Datos institucionales y sedes

La página `/institucion` presenta los datos proporcionados por el colegio y mapas de búsqueda de Google Maps para las siete sedes del directorio institucional. Verifica las direcciones antes de publicar; la página no cambia el catálogo operativo de sedes usado por las citas.
