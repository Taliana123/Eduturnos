# DÍA 5 — REGLAS DE SEGUIMIENTO Y NOTIFICACIONES

## Responsable

Jared

## Objetivo

Definir las reglas que controlan el seguimiento de las citaciones y las notificaciones generadas por el sistema.

## Transiciones de estados

Una citación puede pasar por diferentes estados dependiendo de las acciones realizadas por los usuarios.

### Flujo principal

Pendiente
   ↓
Confirmada
   ↓
Realizada

### Otras transiciones

Pendiente → Cancelada

Confirmada → Cancelada

Pendiente → Reprogramada

Confirmada → Reprogramada

Realizada → No asistió

No asistió → Justificada

## Reglas

1. Una citación nueva inicia en estado Pendiente.
2. El acudiente puede confirmar una citación cuando corresponda.
3. Una citación confirmada puede pasar a Realizada.
4. Una citación puede ser cancelada de acuerdo con los permisos establecidos.
5. Una citación puede ser reprogramada conservando el historial.
6. Una inasistencia debe quedar registrada.
7. Una justificación debe relacionarse con la citación correspondiente.
8. Los cambios importantes deben generar seguimiento.
9. Los recordatorios deben programarse antes de la fecha de la citación.

## Recordatorios

Se contemplan recordatorios de 24 horas y 2 horas antes de la citación.

## Resultado

Se establece un flujo controlado para mantener la trazabilidad de las citaciones.