# EDUTURNOS: organización, equipo y funcionamiento

## Propósito

EDUTURNOS es una aplicación web para organizar las citaciones escolares y su seguimiento. Conecta a docentes, coordinadores, estudiantes y acudientes, y permite consultar la información según el rol y las relaciones académicas de cada usuario.

## Cómo funciona

1. **Acceso:** el usuario se registra o inicia sesión. El sistema valida la cuenta, crea una sesión y determina el rol desde el servidor; el navegador no decide sus permisos.
2. **Contexto institucional:** los módulos usan datos de la institución, sedes, jornadas, grados, grupos, estudiantes, docentes y acudientes.
3. **Citación:** un usuario autorizado registra o consulta una citación con sus participantes, motivo, fecha, hora, lugar y estado. El servidor valida los datos y los guarda en MySQL.
4. **Seguimiento:** las acciones permitidas cambian el estado de la citación. El sistema conserva el historial, quién realizó la acción y cuándo; según el proceso, también genera notificaciones.
5. **Consulta y reportes:** cada persona ve la información que le corresponde. El módulo de reportes filtra citaciones y permite exportar resultados a CSV o Excel.
6. **Funciones complementarias:** calendario, justificaciones, solicitudes, configuración institucional e integración opcional con Google Calendar se ofrecen mediante módulos separados.

## Recorrido técnico

```text
Navegador
	-> proxy HTTPS (cuando está configurado)
	-> Waitress / WSGI
	-> Flask: autenticación y blueprints de cada módulo
	-> MySQL
```

El navegador nunca se conecta directamente a MySQL. Flask aplica controles de sesión, rol y CSRF en las operaciones que modifican datos; los módulos ejecutan las consultas y preparan la respuesta HTML o la descarga solicitada.

## Organización del código activo

- `app.py`, `wsgi.py`: crean la aplicación Flask y registran los módulos.
- `routes/`: autenticación, citas, citaciones, estudiantes, acudientes, docentes, seguimiento, notificaciones, reportes, calendario, configuración y otros módulos.
- `roles.py`, `security.py`: perfiles institucionales, validaciones y controles de seguridad.
- `templates/`: páginas HTML renderizadas con Jinja.
- `static/`: hojas de estilo, JavaScript, iconos y otros recursos.
- `database/`: conexión y preparación del esquema MySQL.
- `servicios/`: lógica compartida, como horarios de citación y correo.
- `sql/`: esquema, migraciones y consultas auxiliares.
- `tests/`: pruebas de rutas, permisos y flujos de la aplicación.
- `docs/`: arquitectura, guías, auditorías y registro de las actividades académicas.
- `tools/maintenance/`: tareas de mantenimiento; no forma parte del flujo normal de cada petición.
- `_archive/` y los archivos `backup*`: material histórico, no necesario para ejecutar la aplicación Flask.

El punto de entrada actual es Flask mediante `wsgi.py`. Los archivos de `api/`, `php/` y las páginas HTML sueltas pertenecen al prototipo PHP/HTML documentado en las primeras clases; no son los blueprints que registra `app.py`.

## Aportes documentados por integrante

La siguiente distribución resume las fichas de `docs/clase-1/` a `docs/clase-6/`. Describe las tareas que el proyecto atribuye en esas entregas; no afirma que cada módulo haya sido trabajo exclusivo de una persona.

### Taliana

- **Interfaz:** preparó la pantalla inicial y la estructura del dashboard.
- **Autenticación:** diseñó las interfaces de registro, inicio de sesión y verificación de cuenta.
- **Citaciones:** preparó las vistas para crear, consultar, ver y editar citaciones.
- **Seguimiento:** diseñó pantallas para consultar estados y notificaciones.
- **Reportes:** preparó la interfaz de filtros para consultar citaciones.

Referencias: `docs/clase-1/taliana-interfaz.md`, `docs/clase-2/taliana-html.md`, `docs/clase-3/taliana-autenticacion.md`, `docs/clase-4/taliana-citaciones.md`, `docs/clase-5/taliana-seguimiento.md`, `docs/clase-6/taliana-reportes.md`.

### Jared

- **Reglas del sistema:** documentó condiciones de usuarios, roles, relaciones académicas y conservación de las citaciones.
- **Autenticación:** definió reglas para registro, verificación, contraseñas, inicio y cierre de sesión.
- **Seguimiento:** especificó transiciones de estado, cancelación, reprogramación, inasistencias y recordatorios.
- **Reportes:** documentó restricciones para que las consultas respeten el rol y el ámbito del usuario.

Referencias: `docs/clase-2/jared-reglas-negocio.md`, `docs/clase-3/jared-autenticacion.md`, `docs/clase-5/jared-seguimiento.md`, `docs/clase-6/jared-reportes.md`.

### Díaz

- **Base de datos:** diseñó y amplió el esquema MySQL, sus tablas, claves y relaciones para usuarios, estructura académica y citaciones.
- **Seguimiento y notificaciones:** documentó las tablas para registrar cambios de estado, responsable, fecha y notificaciones.
- **Reportes:** preparó consultas SQL para resumir citaciones por estado, fechas e inasistencias.

Referencias: `docs/clase-1/diaz-mysql.md`, `docs/clase-2/diaz-mysql.md`, `docs/clase-4/diaz-citaciones.md`, `docs/clase-5/diaz-seguimiento.md`, `docs/clase-6/diaz-reportes.md`.

### Sandy Velasquez Amado

- **Pruebas de datos:** verificó relaciones y restricciones, incluidos documentos y códigos duplicados, usando datos ficticios.
- **Autenticación y citaciones:** documentó pruebas de registro, verificación, inicio de sesión, validaciones de campos, fechas, horarios, edición y cancelación.
- **Seguimiento e integración:** probó el recorrido de una citación desde su creación hasta el resultado, junto con estados, notificaciones, historial y reportes.

Referencias: `docs/clase-2/sandy-datos-pruebas.md`, `docs/clase-3/sandy-pruebas.md`, `docs/clase-4/sandy-pruebas.md`, `docs/clase-5/sandy-pruebas.md`, `docs/clase-6/sandy-pruebas-integracion.md`.

### David Figueroa

- **Backend inicial:** documentó la conexión PHP/MySQL y el flujo de acceso hasta el dashboard.
- **Citaciones:** preparó endpoints del prototipo para crear, consultar, editar y cancelar citaciones.
- **Seguimiento y reportes:** documentó el procesamiento de confirmaciones, reprogramaciones, notificaciones y filtros de reportes.

Referencias: `docs/clase-2/david-backend.md`, `docs/flujo-aplicacion.md`, `docs/clase-4/david-citaciones.md`, `docs/clase-5/david-seguimiento.md`, `docs/clase-6/david-reportes.md`.

### Jaiver Saavedra

- **Presentación visual:** preparó estilos CSS para inicio de sesión, tablas y estados de citaciones.
- **Seguimiento y notificaciones:** organizó visualmente esas interfaces.
- **Reportes:** diseñó tarjetas y estilos adaptables para los reportes.

Referencias: `docs/clase-1/jaiver-interfaz.md`, `docs/clase-4/jaiver-css.md`, `docs/clase-5/jaiver-css.md`, `docs/clase-6/jaiver-reportes.md`.

## Nota sobre las entregas y el estado actual

Las fichas por clase describen etapas de diseño y prototipos: algunas hablan de páginas HTML sueltas, PHP y entregables previstos. La aplicación que ejecuta este repositorio hoy se inicia con Flask/Jinja y los blueprints de `routes/`. Por eso, las fichas sirven para reconocer aportes y decisiones del equipo, pero no deben leerse como un inventario exacto de los archivos activos ni como atribución exclusiva del código actual.

La última verificación local de la suite fue `184 passed, 1 skipped` ejecutando `\.venv\Scripts\python.exe -m pytest -q` en Windows.

## Datos y material local

- `.env` contiene configuración privada y no debe añadirse al repositorio. Conserva el archivo local y comparte únicamente una plantilla sin secretos, como `.env.example`.
- Los respaldos y archivos de `_archive/` se conservan como historial; no se usan para atender peticiones de la aplicación.
