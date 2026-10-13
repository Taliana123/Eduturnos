# Guía final de uso de EDUTURNOS

## Primera vez

1. Extrae el proyecto en una carpeta nueva.
2. Ejecuta `PRIMERA_VEZ.bat`.
3. Configura o verifica MySQL Server.
4. Si necesitas una creación/migración manual, usa `tools/admin/configurar_bd.bat`.
5. Para correo real, configura una cuenta remitente mediante las herramientas de `tools/admin/`.

## Uso diario

Doble clic en `ABRIR_EDUTURNOS.vbs`. También puedes ejecutar `tools/iniciar_eduturnos.bat`.

## Recordatorios

Registra `tools/INSTALAR_RECORDATORIOS.bat` una sola vez. La tarea de Windows ejecuta `tools/ejecutar_recordatorios.bat` cada cinco minutos, sin iniciar schedulers dentro de Flask/Waitress.

## Producción

No uses `127.0.0.1` como enlace para usuarios externos. Despliega EDUTURNOS en un servidor con MySQL central, dominio, HTTPS y SMTP.
