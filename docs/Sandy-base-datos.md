# CLASE 1 - BASE DE DATOS

## Integrante

Sandy

## Área

Capa de datos

## Trabajo realizado

Se documentaron las tablas y los campos
que conforman la estructura inicial de la
base de datos del sistema EDUTURNOS.

## Base de datos

La base de datos utilizada por el sistema es:

- eduturnos

## Tablas y campos

### Tabla usuarios

- id_usuario: identificador único del usuario.
- nombre: nombre del usuario.
- correo: correo electrónico del usuario.
- contrasena: contraseña del usuario.
- rol: rol asignado al usuario.
- estado: estado actual del usuario.

### Tabla estudiantes

- id_estudiante: identificador único del estudiante.
- documento: documento de identidad.
- nombres: nombres del estudiante.
- apellidos: apellidos del estudiante.
- grado: grado del estudiante.
- grupo: grupo del estudiante.

### Tabla acudientes

- id_acudiente: identificador único del acudiente.
- documento: documento de identidad.
- nombres: nombres del acudiente.
- apellidos: apellidos del acudiente.
- telefono: número de teléfono.
- correo: correo electrónico.

### Tabla docentes

- id_docente: identificador único del docente.
- documento: documento de identidad.
- nombres: nombres del docente.
- apellidos: apellidos del docente.
- correo: correo electrónico.

### Tabla motivos

- id_motivo: identificador único del motivo.
- nombre: nombre del motivo de la citación.

### Tabla estados

- id_estado: identificador único del estado.
- nombre: nombre del estado de la citación.

### Tabla citas

- id_cita: identificador único de la cita.
- id_estudiante: estudiante relacionado con la cita.
- id_acudiente: acudiente relacionado con la cita.
- id_docente: docente relacionado con la cita.
- id_motivo: motivo de la cita.
- id_estado: estado de la cita.
- fecha: fecha programada para la cita.
- hora: hora programada para la cita.
- observaciones: información adicional de la cita.

### Tabla notificaciones

- id_notificacion: identificador único de la notificación.
- id_usuario: usuario relacionado con la notificación.
- mensaje: contenido de la notificación.
- fecha_envio: fecha y hora de envío.
- estado: estado de la notificación.

## Resultado

Se documentaron las tablas y los campos
principales de la base de datos EDUTURNOS,
permitiendo identificar la información que
maneja cada tabla dentro del sistema.