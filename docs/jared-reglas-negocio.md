# EDUTURNOS — Reglas de Negocio

## 1. Roles

EDUTURNOS maneja los siguientes roles:

- Super Admin
- Coordinador
- Docente
- Acudiente
- Estudiante
- Invitado

## 2. Estados de citación

Los estados permitidos son:

- Pendiente
- Confirmada
- Realizada
- Cancelada
- Reprogramada
- No asistió
- Justificada

## 3. Creación de una citación

Una citación debe tener:

- Estudiante
- Acudiente
- Docente
- Motivo
- Fecha
- Hora

El estudiante debe estar activo.

El acudiente debe existir y estar relacionado con el estudiante.

El docente debe estar activo.

El motivo es obligatorio.

No se pueden crear citas en fechas pasadas.

## 4. Citas duplicadas

No se debe permitir que un docente tenga dos citas activas en:

- La misma fecha.
- La misma hora.

## 5. Estudiantes retirados

Los estudiantes retirados no pueden generar nuevas solicitudes de citación.

Sus citaciones históricas deben conservarse.

## 6. Modificación

Una modificación debe quedar registrada en:

- seguimiento_citas
- auditoria

## 7. Cancelación

Una cita cancelada conserva su historial.

No se elimina físicamente.

## 8. Reprogramación

Una reprogramación debe:

1. Verificar nueva fecha.
2. Verificar nueva hora.
3. Verificar disponibilidad.
4. Registrar el cambio.
5. Cambiar el estado a Reprogramada.
6. Generar una notificación.

## 9. Confirmación

Una cita Pendiente puede pasar a Confirmada.

La confirmación genera una notificación.

## 10. Seguimiento

Toda modificación importante debe registrar:

- Estado anterior.
- Estado nuevo.
- Observación.
- Usuario responsable.
- Fecha.

## 11. Seguridad

Los usuarios solamente pueden acceder a las funciones correspondientes a su rol.

## 12. Eliminación

No se recomienda eliminar físicamente registros históricos.

Debe utilizarse desactivación o cambio de estado cuando corresponda.