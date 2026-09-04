# CLASE 2 – MYSQL EDUTURNOS

## Responsable

Díaz

## Actividad

Ampliación y estructuración de la base de datos MySQL del sistema EDUTURNOS.

## Descripción

Durante el Día 2 se realizó la ampliación de la base de datos de EDUTURNOS, teniendo en cuenta el crecimiento de la arquitectura general del sistema.

Se diseñó una estructura que permite organizar la información relacionada con usuarios, roles, permisos, instituciones, sedes, jornadas, grados, grupos, periodos académicos, estudiantes, acudientes, docentes y citaciones.

También se incorporaron tablas destinadas al seguimiento de las citaciones, justificaciones, notificaciones, códigos de verificación y auditoría, con el propósito de preparar la base de datos para las funcionalidades que serán desarrolladas posteriormente.

## Trabajo realizado

Se implementaron y organizaron las siguientes tablas:

### Usuarios y permisos

* `usuarios`
* `roles`
* `permisos`
* `rol_permiso`

Estas tablas permiten manejar los usuarios del sistema, sus roles y los permisos asociados a cada rol.

### Institución y estructura académica

* `instituciones`
* `sedes`
* `jornadas`
* `grados`
* `grupos`
* `periodos_academicos`

Estas tablas permiten organizar la información académica e institucional de EDUTURNOS.

### Estudiantes y acudientes

* `estudiantes`
* `acudientes`
* `estudiante_acudiente`

La tabla intermedia `estudiante_acudiente` permite establecer la relación entre los estudiantes y sus acudientes.

### Docentes

* `docentes`
* `asignaciones_docentes`

Estas tablas permiten registrar los docentes y relacionarlos con grados, grupos y periodos académicos.

### Citaciones

* `motivos`
* `estados_cita`
* `citas`

Estas tablas permiten registrar las citaciones, sus motivos, fechas, horas, estados y personas relacionadas.

### Seguimiento y justificaciones

* `seguimiento_citas`
* `justificaciones`

Permiten conservar el historial de cambios realizados en las citaciones y registrar las justificaciones correspondientes.

### Notificaciones y verificación

* `notificaciones`
* `codigos_verificacion`

Estas tablas preparan la base de datos para el sistema de notificaciones y los procesos de verificación de usuarios.

### Auditoría

* `auditoria`

Permite registrar acciones importantes realizadas dentro del sistema, identificando al usuario responsable y el registro afectado.

## Relaciones entre tablas

Se utilizaron claves primarias y claves foráneas para establecer las relaciones entre las diferentes entidades.

Entre las principales relaciones se encuentran:

* Los usuarios pertenecen a un rol.
* Los roles se relacionan con permisos.
* Las sedes pertenecen a una institución.
* Los grupos pertenecen a un grado.
* Los estudiantes pertenecen a una sede, jornada, grado, grupo y periodo académico.
* Los estudiantes pueden relacionarse con uno o varios acudientes.
* Los docentes pertenecen a una sede y jornada.
* Los docentes pueden tener asignaciones académicas.
* Las citaciones se relacionan con estudiantes, acudientes, docentes, motivos y estados.
* El seguimiento se relaciona con las citaciones y los usuarios responsables.
* Las notificaciones pueden relacionarse con usuarios y citaciones.
* Los códigos de verificación pertenecen a usuarios.
* La auditoría permite relacionar las acciones con los usuarios responsables.

## Datos iniciales

Se prepararon datos iniciales para facilitar las pruebas posteriores del sistema.

### Roles

* Super Admin
* Coordinador
* Docente
* Acudiente
* Estudiante
* Invitado

### Jornadas

* Mañana
* Tarde
* Nocturna

### Estados de las citaciones

* Pendiente
* Confirmada
* Realizada
* Cancelada
* Reprogramada
* No asistió
* Justificada

### Motivos

* Académico
* Disciplinario
* Asistencia
* Convivencia
* Orientación

### Grados

* 1° a 11°

## Archivo trabajado

```text
sql/eduturnos.sql
```

## Documentación

```text
docs/clase-2/diaz-mysql.md
```

## Tecnologías utilizadas

* MySQL
* MySQL Workbench
* XAMPP
* Visual Studio Code
* SQL
* Git
* GitHub

## Consideración importante

La estructura desarrollada corresponde a la ampliación arquitectónica del Día 2.

Antes de reemplazar completamente el SQL existente, se debe comparar la nueva estructura con la base de datos que ya se encuentra desarrollada, con el fin de evitar tablas duplicadas, pérdida de información o conflictos entre claves y relaciones.

## Resultado

Se obtuvo una estructura de base de datos ampliada para EDUTURNOS, preparada para soportar la gestión de usuarios, roles, permisos, estudiantes, acudientes, docentes, citaciones, notificaciones, seguimiento y auditoría.

Esta estructura servirá como base para la integración con PHP y el desarrollo de las funcionalidades del sistema en las siguientes etapas del proyecto.
