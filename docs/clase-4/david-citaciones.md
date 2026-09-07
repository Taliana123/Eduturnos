# DÍA 4 — BACKEND DEL MÓDULO DE CITACIONES

## Responsable

David

## Actividad

Conectar el formulario de creación de citaciones con las tablas de la base de datos de EDUTURNOS.

## Descripción del trabajo

Durante el Día 4, me encargué de desarrollar los archivos PHP correspondientes al módulo de citaciones de EDUTURNOS.

Se creó `crear_cita.php`, encargado de recibir los datos enviados desde el formulario de creación de citaciones y realizar las validaciones correspondientes antes de registrar la información en la base de datos.

También se desarrollaron los archivos `listar_citas.php`, `editar_cita.php` y `cancelar_cita.php`, destinados a consultar, modificar y cancelar las citaciones.

El desarrollo utiliza las tablas relacionadas con estudiantes, acudientes, docentes, motivos, estados de citas, citas y seguimiento de citas.

Además, se implementaron validaciones para comprobar la existencia y estado de los registros relacionados antes de realizar las operaciones correspondientes.

## Archivos creados

* `api/crear_cita.php`
* `api/listar_citas.php`
* `api/editar_cita.php`
* `api/cancelar_cita.php`

## Resultado

Se desarrolló la parte inicial del backend del módulo de citaciones, permitiendo conectar las operaciones de creación, consulta, edición y cancelación de citaciones con la base de datos de EDUTURNOS.
