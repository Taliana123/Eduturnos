# CLASE 3 – INTERFAZ Y AUTENTICACIÓN EDUTURNOS

## Responsable

Taliana

## Actividad

Desarrollo de las interfaces iniciales para el registro, inicio de sesión y verificación de cuentas del sistema EDUTURNOS.

## Descripción

Durante el Día 3 se desarrollaron las interfaces correspondientes al proceso de autenticación de usuarios de EDUTURNOS.

Se crearon las páginas necesarias para permitir que los usuarios puedan registrarse, iniciar sesión y verificar su cuenta mediante un código de verificación.

Las interfaces fueron desarrolladas utilizando HTML y JavaScript, manteniendo la estructura visual establecida anteriormente mediante los estilos CSS del proyecto.

## Trabajo realizado

Se desarrollaron las siguientes funcionalidades:

* Interfaz para crear una cuenta.
* Selección del tipo de documento.
* Registro del número de documento.
* Registro de nombres y apellidos.
* Registro del correo electrónico.
* Registro de contraseña.
* Interfaz para verificar una cuenta.
* Campo para ingresar el número de documento.
* Campo para ingresar el código de verificación.
* Interfaz de inicio de sesión.
* Campo para ingresar correo electrónico.
* Campo para ingresar contraseña.
* Validación básica de los campos del formulario.
* Integración inicial de JavaScript para el proceso de autenticación.

## Archivos creados

### Registro

`registro.html`

Contiene el formulario para crear una cuenta de usuario y enviar los datos posteriormente al backend.

### Verificación

`verificar.html`

Contiene el formulario para ingresar el documento y el código de verificación enviado al usuario.

### Inicio de sesión

`login.html`

Contiene el formulario para iniciar sesión mediante correo electrónico y contraseña.

### JavaScript

`js/autenticacion.js`

Contiene las validaciones iniciales del formulario de inicio de sesión y prepara la interfaz para su futura integración con PHP.

## Integración con el backend

Los formularios fueron preparados para comunicarse posteriormente con los archivos PHP encargados de procesar la información.

El registro utiliza:

`api/registro.php`

La verificación utiliza:

`api/verificar.php`

La autenticación mediante JavaScript queda preparada para integrarse posteriormente con el backend.

## Validaciones realizadas

Se implementaron validaciones básicas para comprobar que los campos obligatorios no se encuentren vacíos.

También se utilizaron elementos HTML como:

* `required`
* `type="email"`
* `type="password"`
* `maxlength`

Estas validaciones permiten reducir errores al momento de ingresar información.

## Diseño

Las nuevas páginas utilizan el archivo:

`css/estilos.css`

De esta manera se mantiene la misma apariencia visual establecida para EDUTURNOS y se facilita la continuidad del diseño entre las diferentes interfaces.

## Archivos trabajados

`registro.html`

`verificar.html`

`login.html`

`js/autenticacion.js`

`docs/clase-3/taliana-autenticacion.md`

## Herramientas utilizadas

* HTML5
* JavaScript
* CSS3
* Visual Studio Code
* Git
* GitHub

## Resultado

Se desarrollaron las interfaces iniciales de registro, inicio de sesión y verificación de cuentas de EDUTURNOS.

Las páginas quedaron preparadas para conectarse posteriormente con el backend en PHP y con la base de datos MySQL, permitiendo continuar con el desarrollo del sistema de autenticación.
