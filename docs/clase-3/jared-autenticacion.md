# DÍA 3 — REGLAS DE AUTENTICACIÓN

## Responsable

Jared

## Objetivo

Definir las reglas que controlan el registro, verificación y autenticación de los usuarios de EDUTURNOS.

## Reglas

1. Cada usuario debe tener un número de documento único.
2. Los campos obligatorios deben estar completos.
3. Una cuenta debe estar verificada antes de utilizar el sistema.
4. Una cuenta inactiva no puede iniciar sesión.
5. Las credenciales deben ser validadas antes de permitir el acceso.
6. El usuario debe acceder únicamente a las funciones correspondientes a su rol.
7. La contraseña no debe almacenarse directamente en texto plano.
8. El cierre de sesión debe finalizar la sesión activa.
9. Las páginas internas deben requerir una sesión válida.
10. Los intentos de acceso inválidos deben generar un mensaje de error sin revelar información sensible.

## Roles

EDUTURNOS contempla los roles de:

* Super Admin
* Administrador/Coordinador
* Docente
* Acudiente
* Estudiante
* Visitante

## Resultado

Se establecen las reglas necesarias para controlar el acceso y proteger las funciones internas del sistema. Estas reglas servirán como base para la implementación y validación de los procesos de registro, verificación, inicio y cierre de sesión.
