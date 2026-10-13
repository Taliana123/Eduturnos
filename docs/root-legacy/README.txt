EDUTURNOS - Flask + MySQL

REQUISITOS
- Python 3.11+ recomendado.
- MySQL Server instalado y ejecutándose en Windows.
- MySQL Workbench es opcional; no reemplaza al servidor.

1. Abre esta carpeta en Visual Studio Code.
2. Abre PowerShell en la carpeta del proyecto.
3. Crea el entorno virtual si todavía no existe:
   python -m venv venv
4. Activa el entorno virtual:
   .\venv\Scripts\Activate.ps1
5. Instala las dependencias:
   pip install -r requirements.txt
6. Configura la base de datos:
   python setup_database.py
   El programa pedirá servidor, puerto, usuario y contraseña de MySQL.
7. Configura las credenciales para Flask.
   Puedes usar variables de entorno en PowerShell:
   $env:MYSQL_HOST = "127.0.0.1"
   $env:MYSQL_PORT = "3306"
   $env:MYSQL_USER = "root"
   $env:MYSQL_PASSWORD = "TU_CONTRASENA"
   $env:MYSQL_DATABASE = "eduturnos"
   Si root no tiene contraseña, usa:
   $env:MYSQL_PASSWORD = ""
8. Comprueba la conexión:
   python test_db.py
9. Inicia EDUTURNOS:
   python app.py
10. Abre:
   http://127.0.0.1:5000

NOTA IMPORTANTE SOBRE LA CONTRASEÑA
La contraseña de MySQL NO se escribe como código Python en PowerShell. Se configura como variable de entorno o se solicita de forma segura con setup_database.py.

Si `mysql` no funciona en PowerShell pero MySQL Server sí está instalado, no es un problema de Flask: significa que el ejecutable de MySQL no está agregado al PATH. `setup_database.py` no necesita el comando `mysql`; usa el conector de Python directamente.

REGISTRO DE PRUEBA
- Entra en Registrarse.
- Crea una cuenta.
- El sistema muestra un código de desarrollo.
- Escribe ese código en Verificar cuenta.
- Inicia sesión con documento y contraseña.

ESTRUCTURA PRINCIPAL
- app.py: aplicación Flask.
- config.py: configuración de Flask/MySQL.
- database/db.py: conexión, consultas y escrituras en MySQL.
- setup_database.py: crea y carga la base de datos.
- test_db.py: verifica que Flask puede conectarse.
- sql/eduturnos.sql: estructura y datos iniciales.
- routes/auth.py: registro, verificación, login, logout y dashboard.


=== ARRANQUE RECOMENDADO EN WINDOWS POWERSHELL ===
Abre PowerShell en la carpeta del proyecto y ejecuta:

venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe setup_database.py
venv\Scripts\python.exe test_db.py
venv\Scripts\python.exe app.py

La instalación conserva los datos existentes por defecto. Solo usa
`setup_database.py --recrear` en una base de pruebas que puedas borrar.


NOTA DE INSTALACION
`setup_database.py` crea el esquema que falta y no elimina datos por defecto.
La opción `--recrear` elimina la base completa y debe reservarse para pruebas.

=== AREAS DESARROLLADAS DEL PROYECTO ===
1. Desarrollo Módulo Autenticación
   - Registro y verificación.
   - Inicio de sesión con selección de Estudiante, Docente, Rector o Coordinador.
   - Validación del rol contra MySQL.
   - Gestión de sesión, cierre de sesión y control de acceso por rol.

2. Desarrollo Módulo Reportes
   - Panel de indicadores para Rector/Coordinador.
   - Filtros por fecha y estado.
   - Detalle de citaciones.
   - Exportación de reportes a CSV.

3. Pruebas Unitarias
   - Carpeta tests/ con pruebas automatizadas del módulo de autenticación.
   - Ejecución con pytest.

4. Pruebas de Integración
   - Pruebas Flask/test_client.
   - Prueba de conexión real a MySQL.
   - Ver TESTING.md.

5. Despliegue en Producción
   - wsgi.py preparado.
   - Waitress incluido en requirements.txt.
   - Variables de entorno y guía en PRODUCCION.md.

Para desarrollo en Windows ejecuta desde la carpeta del proyecto:
venv\Scripts\python.exe app.py

Para producción utiliza Waitress según PRODUCCION.md.

FUNCIONALIDADES V7
- Notificaciones por usuario con contador de no leídas, bandeja y marcar como leída.
- Al crear una cita se notifican automáticamente los participantes vinculados y los directivos activos.
- Calendario por rol y descarga de cada cita en formato .ics.
- Módulo de citas con creación para Docente, Rector y Coordinador.


NOTIFICACIONES Y CALENDARIO
- /notificaciones/ muestra notificaciones por usuario y permite marcarlas como leídas.
- /calendario/ muestra las citas visibles según el rol.
- Cada cita permite descargar un archivo .ics.
- Crear o cambiar el estado de una cita genera notificaciones.

AUTENTICACIÓN POR PORTALES Y VERIFICACIÓN INSTITUCIONAL
- Estudiante: documento + contraseña; registro requiere existencia en estudiantes y código de autorización.
- Padre/Madre/Acudiente: documento + contraseña; registro requiere existencia en acudientes y código de autorización.
- Docente: correo institucional + contraseña; registro requiere coincidencia en docentes y código de autorización.
- Coordinación/Rectoría: correo institucional + contraseña; registro requiere código de autorización ligado al rol.
- Los códigos institucionales se generan con generar_codigo_acceso.py y son de un solo uso.
- El servidor determina el rol real desde MySQL; el portal nunca puede cambiar el rol de una cuenta.

MIGRACIÓN DE UNA BD YA EXISTENTE
1) Ejecuta: python upgrade_auth.py
2) Genera códigos con: python generar_codigo_acceso.py
3) No ejecutes setup_database.py sobre una BD que quieras conservar: ese instalador la recrea.

=== AUTENTICACION AUTOMATICA V11 ===
- No usa códigos manuales para registrarse.
- El usuario selecciona su portal, pero el servidor nunca confía en ese dato para asignar el rol.
- Estudiantes: documento + nombres + apellidos + curso se validan contra estudiantes.
- Acudientes: documento + nombres + apellidos + correo se validan contra acudientes.
- Docentes: documento + nombres + apellidos + correo institucional se validan contra docentes.
- Coordinación y Rectoría: se validan contra directorio_institucional.
- El rol de sesión se obtiene exclusivamente de usuarios -> roles en MySQL.
- Ejecuta upgrade_auto_auth.py una sola vez si la base ya existe.
- Para coordinador/rector, el directorio oficial debe cargarse una vez; después el alta de cada usuario es automática.


AUTENTICACION AUTOMATICA
- El inicio de sesión ya no solicita el rol.
- El rol se obtiene de MySQL y controla la autorización.
- El registro valida la identidad contra estudiantes, acudientes, docentes o directorio institucional.
- No se usan códigos de aprobación manual.
- Ejecuta upgrade_security.py una sola vez para habilitar bloqueo temporal por intentos fallidos.

AUTENTICACIÓN DE PERSONAL
- Docentes, Coordinadores y Rectoría deben usar correo institucional @jjfh.edu.co.
- El registro y acceso del personal requieren además el código institucional individual asignado por el colegio y la sede que tiene registrada la persona.
- El código se guarda como hash y no se almacena en texto plano.
- No se requiere aprobación manual en cada registro o inicio de sesión.
