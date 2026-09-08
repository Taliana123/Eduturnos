# DÍA 6 — PRUEBAS FINALES DE INTEGRACIÓN

## Responsable

Sandy

## Actividad

Realizar las pruebas finales de integración del sistema EDUTURNOS.

## Objetivo

Comprobar que los diferentes módulos desarrollados durante los días anteriores puedan funcionar de manera integrada como un solo sistema.

## Descripción del trabajo

Durante el Día 6, me encargué de realizar las pruebas finales de integración de EDUTURNOS.

Se verificaron los principales procesos del sistema, incluyendo la autenticación de usuarios, la administración de citaciones, el seguimiento y las notificaciones, además del módulo de reportes.

Las pruebas permitieron comprobar la relación entre los diferentes procesos y verificar que la información utilizada por cada módulo corresponda con los datos almacenados en la base de datos.

## Pruebas de autenticación

Registro
↓
Verificación
↓
Login
↓
Dashboard

Se comprobó el flujo relacionado con el registro, verificación e inicio de sesión de los usuarios y su acceso al dashboard.

## Pruebas de citaciones

Crear
↓
Consultar
↓
Modificar
↓
Confirmar
↓
Reprogramar
↓
Cancelar

Se verificaron las operaciones principales relacionadas con la administración de las citaciones.

## Pruebas de seguimiento

Citación
↓
Estado
↓
Notificación
↓
Historial

Se comprobó que las citaciones puedan relacionarse con sus estados, notificaciones y registros de seguimiento.

## Pruebas de reportes

Base de datos
↓
Consulta
↓
Filtro
↓
Resultado

Se verificó que la información almacenada en la base de datos pueda ser consultada y filtrada para obtener los resultados de los reportes.

## Archivos creados

* `docs/clase-6/sandy-pruebas-integracion.md`
* `sql/pruebas-integracion.sql`

## Resultado

Se realizaron las pruebas finales de integración de EDUTURNOS, verificando los principales módulos del sistema y la relación entre la información almacenada en la base de datos y las diferentes funcionalidades.
