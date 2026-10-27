# Integraciones opcionales

## Google Calendar

Como alternativa al cliente OAuth web, EDUTURNOS puede usar el puente gratuito de Google
Apps Script para enviar citas a una sola agenda institucional. Requiere una autorización
administrativa inicial y no elimina la necesidad de compartir la agenda con quienes deban
verla o recibir avisos en sus teléfonos. Consulta [Puente gratuito con Google Calendar](./GOOGLE_APPS_SCRIPT.md).

EDUTURNOS mantiene MySQL como fuente oficial y usa una cola persistente para crear, actualizar
y cancelar eventos genéricos en Google Calendar. La sincronización requiere una cuenta
institucional autorizada y una tarea programada en el servidor; los usuarios finales no
necesitan conectar sus cuentas. Los detalles de estudiantes, motivos y observaciones no se
envían a Google. Los pasos de OAuth, variables de entorno, migración, cron, respaldo y
recuperación están en [Google Calendar institucional](./GOOGLE_CALENDAR.md).

## Ayuda privada EDUBOT

EDUBOT está integrado en una tarjeta «Ayuda EDUTURNOS» del menú lateral, antes de «Mi cuenta». Al pulsar la tarjeta se abre el chat; el control × o Escape lo cierra. Cada cierre reinicia la conversación y cancela una respuesta que siga pendiente para que la próxima apertura empiece limpia. En escritorio y móvil aparece como una ventana flotante compacta en la esquina inferior derecha; se puede arrastrar desde el encabezado mientras está abierto, y al cerrar vuelve a su posición inicial. La ventana muestra el saludo sin enfocar automáticamente el campo de texto para no abrir el teclado móvil; toca el campo para empezar a escribir. Responde saludando por el nombre de la cuenta y muestra la conversación en burbujas. Las preguntas frecuentes se contestan localmente; las preguntas abiertas pueden usar Groq mediante `GROQ_API_KEY`, siguiendo instrucciones basadas en las guías confirmadas de EDUTURNOS. EDUBOT no tiene acceso a expedientes ni datos de cuentas.

Las preguntas abiertas se envían a Groq después de ocultar automáticamente algunos correos, números y nombres reconocibles. Esta anonimización no garantiza que toda información personal se detecte: no escribas nombres, documentos, contactos, contraseñas ni datos de estudiantes. La clave se configura solo como variable de entorno del servidor. La cuota gratuita depende de la cuenta y tiene límites; puede agotarse o cambiar, y no garantiza disponibilidad ni respuestas perfectas. EDUBOT no consulta ni modifica registros particulares.

El asistente no consulta expedientes ni datos personales, no debe recibir nombres, documentos ni contraseñas y orienta a la persona a contactar a coordinación cuando la consulta requiere revisar un caso concreto. Las respuestas son informativas y no sustituyen los canales institucionales.

## Chatbot público con Beepy

`BEEPY_ENABLED=1` conserva el widget Beepy únicamente en la portada pública. `BEEPY_DOMAINS` acepta una lista de dominios separados por comas autorizados en Beepy; también se admite `BEEPY_DOMAIN` para conservar la configuración anterior. La portada carga el script solo en los dominios permitidos, como `seventy-excavator-designate.ngrok-free.dev` y `eduturnos-jjfh.alwaysdata.net`. Si cambia el dominio ngrok o la cuenta de Beepy, revisa sus dominios autorizados e identificadores. Esta integración es independiente del asistente privado EDUBOT, que funciona localmente dentro de EDUTURNOS.

## Datos institucionales y sedes

La página `/institucion` presenta los datos proporcionados por el colegio y mapas de búsqueda de Google Maps para las siete sedes del directorio institucional. Verifica las direcciones antes de publicar; la página no cambia el catálogo operativo de sedes usado por las citas.
