# DÍA 6 — BACKEND DE REPORTES

## Responsable

David

## Actividad

Desarrollo del backend para la consulta de reportes de las citaciones de EDUTURNOS.

## Descripción del trabajo

Durante el Día 6, me encargué de desarrollar el archivo `api/reportes.php`, encargado de procesar las consultas de reportes del sistema EDUTURNOS.

El archivo permite recibir filtros de fecha inicial, fecha final y estado de la citación mediante el método `GET`.

También se implementó una consulta a la tabla `citas`, permitiendo obtener las citaciones de acuerdo con los filtros seleccionados. Los resultados son organizados por fecha y hora de manera descendente.

Además, se verificó que el usuario tenga una sesión activa antes de permitir el acceso al reporte.

## Archivo creado

`api/reportes.php`

## Trabajo realizado

* Validación de sesión del usuario.
* Recepción de filtros mediante `GET`.
* Filtro por fecha inicial.
* Filtro por fecha final.
* Filtro por estado.
* Consulta de las citaciones almacenadas.
* Ordenamiento por fecha y hora.
* Preparación de los resultados del reporte.

## Resultado

Se desarrolló el backend inicial del módulo de reportes de EDUTURNOS, permitiendo consultar las citaciones utilizando filtros de fecha y estado y dejando preparada la integración con la interfaz de reportes.
