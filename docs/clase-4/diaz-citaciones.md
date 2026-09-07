# DÍA 4 — BASE DE DATOS DEL MÓDULO DE CITACIONES

## Responsable

Díaz

## Actividad

Desarrollo de la estructura de base de datos necesaria para el módulo de citaciones de EDUTURNOS.

## Descripción del trabajo

Durante el Día 4, me encargué de complementar la base de datos existente de EDUTURNOS con las estructuras necesarias para administrar las citaciones.

Se creó el archivo `sql/citaciones.sql`, donde se definieron las tablas `motivos`, `estados_cita` y `citas`.

La tabla `motivos` permite almacenar los diferentes motivos por los cuales se genera una citación. La tabla `estados_cita` permite controlar los diferentes estados que puede presentar una cita durante su proceso.

La tabla `citas` almacena la información principal de cada citación, incluyendo el estudiante, acudiente, docente, motivo, estado, fecha, hora, lugar y observaciones.

También se establecieron claves foráneas para relacionar las citaciones con las tablas existentes de `estudiantes`, `acudientes` y `docentes`, además de las tablas de motivos y estados.

De esta manera, la nueva estructura se integra con la base de datos desarrollada en los días anteriores sin crear nuevamente las tablas que ya existen.

## Archivo creado

`sql/citaciones.sql`

## Trabajo realizado

* Creación de la tabla `motivos`.
* Creación de la tabla `estados_cita`.
* Creación de la tabla `citas`.
* Configuración de claves primarias.
* Configuración de claves foráneas.
* Relación con estudiantes.
* Relación con acudientes.
* Relación con docentes.
* Relación con motivos.
* Relación con estados de las citaciones.

## Resultado

Se complementó la base de datos de EDUTURNOS con la estructura necesaria para almacenar y administrar las citaciones, manteniendo las relaciones con las tablas creadas anteriormente.
