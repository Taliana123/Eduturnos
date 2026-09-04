# CLASE 2 – DATOS Y PRUEBAS EDUTURNOS

## Responsable

Sandy

## Actividad

Validación de la estructura de la base de datos y realización de pruebas con datos ficticios.

## Descripción

Durante el Día 2, Sandy se encargó de verificar el funcionamiento de la estructura de la base de datos desarrollada para EDUTURNOS.

El objetivo fue comprobar que las tablas, relaciones y restricciones funcionaran correctamente mediante diferentes pruebas con datos ficticios.

## Trabajo realizado

Se realizaron pruebas sobre:

* Creación de instituciones.
* Creación de sedes.
* Creación de jornadas.
* Creación de grados.
* Creación de grupos.
* Registro de estudiantes.
* Registro de acudientes.
* Relación entre estudiantes y acudientes.
* Registro de docentes.
* Creación de citaciones.
* Cambio de estados de las citaciones.
* Registro de seguimiento.
* Creación de notificaciones.
* Registro de auditoría.

También se realizaron consultas SQL para verificar que los datos fueran almacenados correctamente.

## Pruebas de restricciones

Se verificaron las restricciones relacionadas con datos duplicados.

Se comprobó que no se deben permitir registros duplicados en:

* Documento de identificación.
* Código estudiantil.

## Datos de prueba

Para las pruebas se utilizaron datos ficticios y no se utilizaron datos reales de estudiantes.

Se utilizaron como datos de prueba:

* Institución Educativa José Joaquín Flórez Hernández.
* Sede Principal.
* Picaleña.
* Bello Horizonte.
* Jornada mañana.
* Jornada tarde.
* Jornada nocturna.
* Grados académicos.
* Grupos de prueba.

## Grupos académicos

Se verificó la estructura inicial para trabajar con 6 grupos por grado.

Para el grado 10 se contemplaron inicialmente:

* 10-1
* 10-2
* 10-3
* 10-4
* 10-5
* 10-6

La estructura queda preparada para ampliar posteriormente hasta 8 grupos por grado cuando la institución lo requiera.

## Consultas realizadas

Se realizaron consultas SQL para comprobar:

* Instituciones registradas.
* Sedes registradas.
* Jornadas registradas.
* Grados registrados.
* Grupos registrados.
* Roles del sistema.
* Estados de las citaciones.
* Motivos de las citaciones.
* Existencia de registros duplicados.

## Archivos trabajados

`sql/pruebas-sandy.sql`

`docs/clase-2/sandy-datos-pruebas.md`

## Herramientas utilizadas

* MySQL
* MySQL Workbench
* XAMPP
* Visual Studio Code
* SQL
* Git
* GitHub

## Resultado

Se realizaron las pruebas iniciales de la base de datos EDUTURNOS utilizando información ficticia.

Las pruebas permitieron verificar la organización de los datos, las relaciones entre las tablas y las restricciones necesarias para evitar registros duplicados.

La base de datos queda preparada para continuar con las pruebas y la integración con las funcionalidades del sistema.
