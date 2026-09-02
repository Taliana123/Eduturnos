# CLASE 2 – BACKEND EDUTURNOS

## Responsable

David

## Actividad

Preparación de la conexión entre PHP y MySQL para el sistema EDUTURNOS.

## Descripción

Durante el Día 2 se desarrolló la configuración inicial del backend de EDUTURNOS, estableciendo la conexión entre PHP y la base de datos MySQL.

Se creó un archivo de conexión que utiliza la extensión `mysqli` de PHP para establecer comunicación con la base de datos `eduturnos`.

También se creó un archivo de prueba para comprobar que la conexión entre PHP y MySQL funciona correctamente.

## Trabajo realizado

* Configuración del servidor local.
* Configuración del usuario de MySQL.
* Configuración de la base de datos EDUTURNOS.
* Creación de la conexión mediante `mysqli`.
* Configuración de codificación `utf8mb4`.
* Manejo básico de errores de conexión.
* Creación de un archivo para probar la conexión.

## Archivos trabajados

```text
php/config/conexion.php
php/config/prueba_conexion.php
docs/clase-2/david-backend.md
```

## Prueba en XAMPP

La conexión será probada utilizando el servidor Apache de XAMPP y MySQL.

Ruta de prueba:

```text
http://localhost/Eduturnos/php/config/prueba_conexion.php
```

## Resultado esperado

Al ingresar a la ruta de prueba debe aparecer:

```text
Conexión exitosa con EDUTURNOS.
```

## Tecnologías utilizadas

* PHP
* MySQL
* XAMPP
* Visual Studio Code
* Git
* GitHub

## Resultado

Se preparó la conexión inicial entre PHP y MySQL, dejando establecida la base necesaria para que las funcionalidades del sistema EDUTURNOS puedan comunicarse posteriormente con la base de datos.
