# Backups

Usa `BACKUP_BD_EDUTURNOS.bat` para crear un respaldo local de MySQL. Antes de producción, configura un almacenamiento externo y prueba restaurar periódicamente un backup.

## Respaldo diario en Windows

Ejecuta `tools/admin/instalar_respaldo_diario.ps1` para programar un respaldo diario a las 23:00 con el entorno `.venv` del proyecto. La tarea se ejecuta cuando la cuenta actual ha iniciado sesión; el equipo y MySQL deben estar disponibles.

Los archivos se guardan en `data/private/backups`, junto con un checksum SHA-256. Esa carpeta contiene información personal: no la publiques ni la sincronices a repositorios. El script `tools/admin/respaldo.py --verificar <archivo>` valida la integridad y `--probar-restauracion` verifica la copia en una base temporal.

El respaldo local protege frente a errores de la aplicación, pero no frente a la pérdida o daño del mismo disco. Conserva también una copia cifrada fuera del equipo según la política de privacidad del colegio.
