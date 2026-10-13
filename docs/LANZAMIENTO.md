# EDUTURNOS - LISTA DE LANZAMIENTO

## A. Aplicación
- [x] Arquitectura Flask por módulos/blueprints
- [x] Roles y autorización en servidor
- [x] Citas, seguimiento y justificaciones
- [x] Notificaciones y calendario
- [x] Reportes y auditoría
- [x] CSRF, sesiones y cabeceras de seguridad
- [x] Health check
- [x] Docker local y Docker de producción
- [x] Scripts de doble clic en Windows
- [x] Cinco casos DEMO separados de producción

## B. Infraestructura externa
- [ ] Servidor de producción 24/7
- [ ] MySQL central persistente
- [ ] Dominio/subdominio
- [ ] DNS
- [ ] HTTPS
- [ ] SMTP institucional si se requiere correo
- [ ] Backups externos automáticos
- [ ] Prueba de restauración
- [ ] Monitoreo y alertas

## C. Datos institucionales
- [ ] Cargar sedes oficiales
- [ ] Cargar estudiantes y acudientes oficiales
- [ ] Cargar docentes/coordinadores/rector en `directorio_institucional`
- [ ] Asignar códigos institucionales individuales de forma segura
- [ ] No distribuir credenciales DEMO en producción

## D. Pruebas antes de abrir
- [ ] Cinco casos funcionales en staging
- [ ] Registro y login de los cinco roles
- [ ] Autorización negativa: cada rol intentando entrar a módulos no permitidos
- [ ] Citas y prevención de dobles reservas
- [ ] Confirmación, seguimiento y justificación
- [ ] Notificaciones y calendario
- [ ] Reporte/CSV
- [ ] Recuperación de contraseña con SMTP real
- [ ] Backup + restauración
- [ ] HTTPS y cookies seguras
- [ ] Prueba básica de concurrencia

NO declarar producción completa hasta cerrar los puntos externos y ejecutar pruebas en staging.
