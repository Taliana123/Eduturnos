# FLUJO DE LA APLICACIÓN – EDUTURNOS

## Responsable

David

## Clase

Clase 2 – Aplicación

## Descripción

En esta actividad se documentó el flujo básico de funcionamiento de la aplicación EDUTURNOS. En esta etapa todavía no se desarrolla toda la programación en PHP, sino que se establece el proceso que seguirá el usuario dentro del sistema.

## Flujo de la aplicación

```text
Usuario
   ↓
Login
   ↓
Validación
   ↓
Rol
   ↓
Permisos
   ↓
Dashboard
```

## Descripción de cada etapa

### 1. Usuario

El usuario ingresa al sistema EDUTURNOS para acceder a las funciones correspondientes a su perfil.

### 2. Login

El usuario introduce sus datos de acceso en el formulario de inicio de sesión.

### 3. Validación

El sistema verifica que los datos ingresados sean correctos antes de permitir el acceso.

### 4. Rol

Después de validar al usuario, el sistema identifica el rol que tiene asignado.

### 5. Permisos

Según el rol del usuario, el sistema determina las funciones y opciones a las que puede acceder.

### 6. Dashboard

Finalmente, el usuario ingresa al Dashboard y visualiza las opciones disponibles según sus permisos.

## Resultado

Se estableció el flujo básico que seguirá EDUTURNOS desde el inicio de sesión hasta el acceso al Dashboard. Esta estructura servirá como base para implementar posteriormente la lógica de autenticación y permisos mediante PHP.

## Archivo creado

`docs/flujo-aplicacion.md`

## Control de versiones

La documentación será registrada mediante Git y subida al repositorio de EDUTURNOS en la rama `nueva-historia`.
