# EDUTURNOS

Sistema web institucional para gestionar citaciones escolares, solicitudes, calendario, notificaciones, seguimiento, justificaciones, reportes y auditoría.

## Arranque en Windows

Primera instalación: ejecuta `PRIMERA_VEZ.bat`.

Uso diario: doble clic en `ABRIR_EDUTURNOS.vbs`. El lanzador usa `tools/iniciar_eduturnos.bat` internamente.

## Base de datos y administración

Las tareas técnicas están en `tools/admin/`. Para configurar la base usa `tools/admin/configurar_bd.bat`. Para tareas de correo usa los scripts equivalentes de esa carpeta.

## Recordatorios

Los recordatorios de 24 horas y 2 horas se ejecutan como proceso independiente de Flask/Waitress y usan MySQL directamente. Ejecuta manualmente `tools/ejecutar_recordatorios.bat` o registra la tarea de Windows con `tools/INSTALAR_RECORDATORIOS.bat`.

## Pruebas

Con el entorno virtual creado, usa `tools/probar_todo.bat`. La prueba contra MySQL real requiere un servidor MySQL accesible y una configuración `.env` válida.

## Producción multiusuario

Para varios dispositivos, despliega EDUTURNOS en un servidor con MySQL central, HTTPS, dominio y SMTP. Los usuarios finales no necesitan instalar Python ni MySQL.

## Seguridad

No distribuyas `.env`, contraseñas, logs ni datos reales. El proyecto incluye `.env.example` para la configuración inicial.

## Integraciones

Google Calendar y la ayuda Gemini son opcionales; consulta [docs/INTEGRACIONES.md](docs/INTEGRACIONES.md) para configurar HTTPS, OAuth y sus variables locales.
