# DÍA 5 — BASE DE DATOS DE SEGUIMIENTO Y NOTIFICACIONES

## Responsable

Díaz

## Actividad

Crear las estructuras de base de datos necesarias para el seguimiento de las citaciones y las notificaciones de EDUTURNOS.

## Descripción del trabajo

Durante el Día 5, me encargué de complementar la base de datos de EDUTURNOS con las estructuras necesarias para registrar el seguimiento de las citaciones y las notificaciones generadas por el sistema.

Se creó la tabla `seguimiento_citas`, encargada de almacenar los cambios de estado de las citaciones, el motivo del cambio, el usuario responsable y la fecha y hora en que se realizó.

También se creó la tabla `notificaciones`, destinada a almacenar las notificaciones relacionadas con los usuarios y las citaciones, incluyendo el título, mensaje, tipo, estado de lectura y fecha de envío.

La tabla `seguimiento_citas` se relaciona con la tabla `citas` mediante una clave foránea, permitiendo mantener la relación entre cada seguimiento y la citación correspondiente.

## Trabajo realizado

* Creación de la tabla `seguimiento_citas`.
* Configuración de la clave primaria de seguimiento.
* Relación entre `seguimiento_citas` y `citas`.
* Registro del estado anterior y estado nuevo de una citación.
* Registro del motivo del cambio.
* Registro del usuario responsable.
* Registro de fecha y hora del seguimiento.
* Creación de la tabla `notificaciones`.
* Registro del usuario relacionado con la notificación.
* Relación de las notificaciones con las citaciones.
* Registro de título y mensaje.
* Registro del tipo de notificación.
* Control del estado de lectura.
* Registro de la fecha de envío.

## Archivo creado

`sql/seguimiento-notificaciones.sql`

## Resultado

Se complementó la base de datos de EDUTURNOS con las tablas necesarias para registrar el seguimiento de las citaciones y almacenar las notificaciones generadas por el sistema.
