# CLASE 2 – REGLAS DE NEGOCIO EDUTURNOS

## Responsable

Jared

## Actividad

Documentación y preparación de las reglas de negocio del sistema EDUTURNOS.

## Descripción

Durante la Clase 2, Jared se encargó de identificar y documentar las principales reglas de negocio que deberán ser tenidas en cuenta durante el desarrollo del sistema EDUTURNOS.

Estas reglas permiten establecer las condiciones que deben cumplirse para garantizar el correcto funcionamiento de los usuarios, estudiantes, acudientes, docentes y citaciones.

## Reglas de negocio

### RB-001

Un usuario debe tener un rol.

### RB-002

Una cuenta debe estar activa para iniciar sesión.

### RB-003

Un estudiante debe tener identificación única.

### RB-004

Un acudiente puede estar relacionado con uno o varios estudiantes.

### RB-005

Una citación debe estar asociada a un estudiante.

### RB-006

Una citación debe tener fecha y hora.

### RB-007

No se permiten citas duplicadas.

### RB-008

Una cita cancelada debe conservarse en el historial.

### RB-009

Una cita realizada no debe eliminarse físicamente.

### RB-010

Un docente solo puede gestionar las citaciones autorizadas.

### RB-011

Un acudiente solo puede consultar sus relaciones autorizadas.

### RB-012

Los cambios importantes deben quedar registrados en auditoría.

### RB-013

Un estudiante no puede modificar información administrativa.

### RB-014

Los permisos dependen del rol.

### RB-015

Las sedes y jornadas deben estar relacionadas correctamente.

## Estados de las citaciones

El sistema contempla los siguientes estados:

* Pendiente
* Confirmada
* Realizada
* Cancelada
* Reprogramada
* No asistió
* Justificada

## Aplicación de las reglas

Las reglas documentadas servirán como referencia para el desarrollo posterior de las funcionalidades del sistema, especialmente en la gestión de usuarios, roles, permisos, estudiantes, acudientes y citaciones.

Estas condiciones podrán ser implementadas posteriormente mediante PHP y la base de datos MySQL.

## Archivo trabajado

```text
docs/clase-2/jared-reglas-negocio.md
```

## Tecnologías y herramientas utilizadas

* Visual Studio Code
* Markdown
* Git
* GitHub

## Resultado

Se documentaron las reglas principales de negocio y los estados de las citaciones de EDUTURNOS, dejando una guía para que las futuras funcionalidades del sistema respeten las condiciones establecidas.
