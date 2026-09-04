# DÍA 3 — PRUEBAS DE AUTENTICACIÓN

## Responsable

Sandy

## Objetivo

Realizar pruebas sobre los procesos de registro, verificación, inicio y cierre de sesión del sistema EDUTURNOS.

## Descripción del trabajo

Durante el Día 3, me encargué de diseñar y realizar las pruebas relacionadas con el módulo de autenticación de EDUTURNOS.

Se creó el archivo `sql/pruebas-autenticacion.sql`, donde se incluyeron diferentes consultas e instrucciones SQL para comprobar el comportamiento de la base de datos frente a situaciones correctas e incorrectas.

## Pruebas realizadas

1. **Registro correcto:** se comprobó el registro de un usuario utilizando datos válidos.
2. **Documento duplicado:** se verificó que no sea posible registrar dos usuarios con el mismo documento.
3. **Correo duplicado:** se comprobó la restricción de correo electrónico único.
4. **Verificación correcta:** se realizó una prueba utilizando un código de verificación válido.
5. **Código incorrecto:** se comprobó el comportamiento cuando se utiliza un código diferente al registrado.
6. **Login correcto:** se verificó la consulta de un usuario con estado activo.
7. **Contraseña incorrecta:** se comprobó la existencia del usuario para posteriormente realizar la validación de contraseña mediante PHP.
8. **Usuario inexistente:** se verificó que una búsqueda con un documento no registrado no devuelva resultados.
9. **Usuario inactivo:** se comprobó que un usuario con estado `Inactivo` no aparezca como usuario disponible para iniciar sesión.
10. **Cierre de sesión:** se verificó el usuario utilizado durante las pruebas, dejando la finalización de la sesión para el proceso correspondiente en PHP.

## Archivo creado

`sql/pruebas-autenticacion.sql`

## Herramientas utilizadas

* MySQL
* MySQL Workbench
* XAMPP
* Visual Studio Code
* SQL
* Git
* GitHub

## Resultado

Se diseñaron pruebas para validar los principales escenarios del sistema de autenticación. Las pruebas permiten identificar registros duplicados, usuarios inexistentes o inactivos y problemas relacionados con la verificación de cuentas, dejando una base para comprobar posteriormente la integración entre MySQL y PHP.
