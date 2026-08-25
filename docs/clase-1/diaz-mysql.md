# CLASE 1 - MYSQL

## Integrante
Díaz

## Área
Capa de datos

## Trabajo realizado

Se creó la estructura inicial de la base de datos
MySQL del sistema EDUTURNOS mediante el archivo
`sql/eduturnos.sql`.

## Base de datos

Se definió la base de datos:

- eduturnos

## Tablas creadas

Se crearon las siguientes tablas:

- usuarios.
- estudiantes.
- acudientes.
- docentes.
- motivos.
- estados.
- citas.
- notificaciones.

## Relaciones

La tabla `citas` contiene relaciones mediante
claves foráneas con las tablas:

- estudiantes.
- acudientes.
- docentes.
- motivos.
- estados.

La tabla `notificaciones` contiene una relación
mediante clave foránea con la tabla `usuarios`.

## Resultado

Se creó el archivo `sql/eduturnos.sql` con la
estructura inicial de la base de datos EDUTURNOS,
incluyendo sus tablas y relaciones principales.