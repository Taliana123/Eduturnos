from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parent

ARCHIVO = BASE / "templates" / "dashboard.html"
BACKUP = BASE / "templates" / "dashboard.html.backup_organizado"

if not ARCHIVO.exists():
    print("[ERROR] No existe templates/dashboard.html")
    raise SystemExit(1)

# ------------------------------------------------------------
# COPIA DE SEGURIDAD
# ------------------------------------------------------------

shutil.copy2(ARCHIVO, BACKUP)

# ------------------------------------------------------------
# DASHBOARD NUEVO
# Se conserva toda la lógica Jinja existente.
# ------------------------------------------------------------

HTML = r'''{% extends 'base.html' %}

{% block title %}Panel · EDUTURNOS{% endblock %}

{% block content %}

<section class="dashboard-page">

    <!-- =====================================================
         ENCABEZADO
         ===================================================== -->

    <div class="dashboard-head">

        <div class="dashboard-head-info">

            <span class="badge">
                {{ usuario.rol_nombre }}
            </span>

            <h1>
                Hola, {{ usuario.nombres }} {{ usuario.apellidos }}
            </h1>

            <p class="muted">
                Información y accesos según tu rol institucional.
            </p>

        </div>

        <div class="dashboard-head-action">

            <a
                class="boton boton-danger dashboard-logout"
                href="{{ url_for('auth.logout') }}"
            >
                Cerrar sesión
            </a>

        </div>

    </div>


    <!-- =====================================================
         INDICADORES
         ===================================================== -->

    <section class="dashboard-kpis">

        <article class="dashboard-kpi">
            <span>Total de citas</span>
            <strong>{{ datos.total_citas }}</strong>
        </article>

        <article class="dashboard-kpi">
            <span>Pendientes</span>
            <strong>{{ datos.pendientes }}</strong>
        </article>

        <article class="dashboard-kpi">
            <span>Confirmadas</span>
            <strong>{{ datos.confirmadas }}</strong>
        </article>

        <article class="dashboard-kpi">
            <span>Notificaciones sin leer</span>
            <strong>{{ notificaciones_no_leidas }}</strong>
        </article>

    </section>


    <!-- =====================================================
         CONTENIDO
         ===================================================== -->

    <div class="dashboard-main">

        <!-- ACCIONES -->
        <section class="dashboard-card dashboard-actions-card">

            <div class="dashboard-card-head">

                <div>
                    <span class="badge">Accesos</span>

                    <h2>Acciones rápidas</h2>

                    <p class="muted">
                        Accede directamente a las funciones disponibles para tu rol.
                    </p>
                </div>

            </div>


            <div class="dashboard-action-grid">

                <!-- CITAS -->

                <a
                    class="dashboard-action"
                    href="{{ url_for('citas.index') }}"
                >

                    <div class="dashboard-action-top">
                        <span class="dashboard-action-icon">
                            Citas
                        </span>
                    </div>

                    <h3>Citas</h3>

                    <p>
                        Consultar y gestionar citaciones.
                    </p>

                    <span class="dashboard-action-link">
                        Ver citas →
                    </span>

                </a>


                <!-- CALENDARIO -->

                <a
                    class="dashboard-action"
                    href="{{ url_for('calendario.index') }}"
                >

                    <div class="dashboard-action-top">
                        <span class="dashboard-action-icon">
                            Calendario
                        </span>
                    </div>

                    <h3>Calendario</h3>

                    <p>
                        Revisar fechas y horarios.
                    </p>

                    <span class="dashboard-action-link">
                        Abrir calendario →
                    </span>

                </a>


                <!-- NOTIFICACIONES -->

                <a
                    class="dashboard-action"
                    href="{{ url_for('notificaciones.index') }}"
                >

                    <div class="dashboard-action-top">
                        <span class="dashboard-action-icon">
                            Avisos
                        </span>
                    </div>

                    <h3>Notificaciones</h3>

                    <p>
                        Ver avisos y novedades del sistema.
                    </p>

                    {% if notificaciones_no_leidas > 0 %}

                    <span class="dashboard-action-link">
                        {{ notificaciones_no_leidas }} sin leer →
                    </span>

                    {% else %}

                    <span class="dashboard-action-link">
                        Ver notificaciones →
                    </span>

                    {% endif %}

                </a>


                <!-- SOLICITUDES -->

                {% if usuario.rol_nombre in [
                    'Docente',
                    'Administrador / Coordinador',
                    'Rector',
                    'Super Admin'
                ] %}

                <a
                    class="dashboard-action"
                    href="{{ url_for('solicitudes.index') }}"
                >

                    <div class="dashboard-action-top">
                        <span class="dashboard-action-icon">
                            Solicitudes
                        </span>
                    </div>

                    <h3>Solicitudes</h3>

                    <p>
                        Gestionar reuniones y propuestas.
                    </p>

                    <span class="dashboard-action-link">
                        Ver solicitudes →
                    </span>

                </a>

                {% endif %}


                <!-- REPORTES -->

                {% if usuario.rol_nombre in [
                    'Administrador / Coordinador',
                    'Rector',
                    'Super Admin'
                ] %}

                <a
                    class="dashboard-action"
                    href="{{ url_for('reportes.index') }}"
                >

                    <div class="dashboard-action-top">
                        <span class="dashboard-action-icon">
                            Reportes
                        </span>
                    </div>

                    <h3>Reportes</h3>

                    <p>
                        Consultar indicadores institucionales.
                    </p>

                    <span class="dashboard-action-link">
                        Ver reportes →
                    </span>

                </a>

                {% endif %}


                <!-- JUSTIFICACIONES -->

                {% if usuario.rol_nombre in [
                    'Estudiante',
                    'Acudiente'
                ] %}

                <a
                    class="dashboard-action"
                    href="{{ url_for('justificaciones.index') }}"
                >

                    <div class="dashboard-action-top">
                        <span class="dashboard-action-icon">
                            Justificaciones
                        </span>
                    </div>

                    <h3>Justificaciones</h3>

                    <p>
                        Consultar o presentar solicitudes.
                    </p>

                    <span class="dashboard-action-link">
                        Ver justificaciones →
                    </span>

                </a>

                {% endif %}

            </div>

        </section>


        <!-- CUENTA -->

        <section class="dashboard-card dashboard-account-card">

            <div class="dashboard-card-head">

                <div>
                    <span class="badge">Cuenta</span>

                    <h2>Mi cuenta</h2>
                </div>

            </div>

            <p class="muted dashboard-account-text">
                Mantén una contraseña personal segura y actualizada.
            </p>

            <div class="dashboard-account-action">

                <a
                    class="boton boton-full"
                    href="{{ url_for('passwords.cambiar_password') }}"
                >
                    Cambiar contraseña
                </a>

            </div>

        </section>

    </div>

</section>


<style>

/* =========================================================
   EDUTURNOS - DASHBOARD ORGANIZADO
   ========================================================= */

.dashboard-page {
    width: 100%;
    max-width: 1180px;

    margin: 0 auto;

    padding: 10px 0 35px;

    box-sizing: border-box;
}

/* =========================================================
   ENCABEZADO
   ========================================================= */

.dashboard-head {
    width: 100%;

    display: flex;

    justify-content: space-between;
    align-items: flex-start;

    gap: 25px;

    margin-bottom: 24px;

    box-sizing: border-box;
}

.dashboard-head-info {
    min-width: 0;
}

.dashboard-head-info h1 {
    margin: 8px 0 8px;

    color: #0f172a;

    font-size: 30px;

    line-height: 1.2;
}

.dashboard-head-info p {
    margin: 0;

    line-height: 1.5;
}

.dashboard-head-action {
    flex-shrink: 0;
}

.dashboard-logout {
    white-space: nowrap;
}

/* =========================================================
   INDICADORES
   ========================================================= */

.dashboard-kpis {
    display: grid;

    grid-template-columns:
        repeat(4, minmax(0, 1fr));

    gap: 16px;

    width: 100%;

    margin-bottom: 24px;
}

.dashboard-kpi {
    min-width: 0;

    padding: 20px;

    background: #ffffff;

    border: 1px solid #dbe3ec;

    border-radius: 12px;

    box-shadow:
        0 2px 7px rgba(15, 23, 42, 0.05);

    box-sizing: border-box;
}

.dashboard-kpi span {
    display: block;

    margin-bottom: 8px;

    color: #64748b;

    font-size: 13px;

    line-height: 1.35;
}

.dashboard-kpi strong {
    display: block;

    color: #0f172a;

    font-size: 27px;

    line-height: 1.1;

    font-weight: 700;
}

/* =========================================================
   CONTENEDORES
   ========================================================= */

.dashboard-main {
    width: 100%;

    display: grid;

    grid-template-columns:
        minmax(0, 1fr);

    gap: 20px;
}

.dashboard-card {
    width: 100%;

    padding: 24px;

    background: #ffffff;

    border: 1px solid #dbe3ec;

    border-radius: 14px;

    box-shadow:
        0 3px 9px rgba(15, 23, 42, 0.05);

    box-sizing: border-box;
}

/* =========================================================
   ENCABEZADO DE CADA TARJETA
   ========================================================= */

.dashboard-card-head {
    width: 100%;

    margin-bottom: 20px;
}

.dashboard-card-head h2 {
    margin: 8px 0 7px;

    color: #0f172a;

    font-size: 22px;

    line-height: 1.2;
}

.dashboard-card-head p {
    margin: 0;

    line-height: 1.5;
}

/* =========================================================
   ACCIONES RÁPIDAS
   ========================================================= */

.dashboard-action-grid {
    width: 100%;

    display: grid;

    grid-template-columns:
        repeat(4, minmax(0, 1fr));

    gap: 16px;

    align-items: stretch;
}

.dashboard-action {
    min-width: 0;

    min-height: 190px;

    padding: 18px;

    display: flex;

    flex-direction: column;

    align-items: stretch;

    justify-content: flex-start;

    text-decoration: none;

    background: #f8fafc;

    border: 1px solid #dbe3ec;

    border-radius: 11px;

    box-sizing: border-box;

    transition:
        transform 0.15s ease,
        border-color 0.2s ease,
        box-shadow 0.2s ease,
        background 0.2s ease;
}

.dashboard-action:hover {
    transform: translateY(-2px);

    background: #ffffff;

    border-color: #bfdbfe;

    box-shadow:
        0 7px 18px rgba(15, 23, 42, 0.08);
}

.dashboard-action-top {
    width: 100%;

    margin-bottom: 15px;
}

.dashboard-action-icon {
    display: inline-flex;

    align-items: center;

    min-height: 30px;

    padding: 6px 10px;

    border-radius: 7px;

    background: #eaf2ff;

    color: #2563eb;

    font-size: 12px;

    font-weight: 600;

    line-height: 1;
}

.dashboard-action h3 {
    margin: 0 0 8px;

    color: #0f172a;

    font-size: 18px;

    line-height: 1.2;
}

.dashboard-action p {
    flex: 1;

    margin: 0;

    color: #64748b;

    font-size: 13.5px;

    line-height: 1.45;
}

.dashboard-action-link {
    display: block;

    margin-top: 16px;

    color: #2563eb;

    font-size: 13px;

    font-weight: 600;

    line-height: 1.3;
}

/* =========================================================
   MI CUENTA
   ========================================================= */

.dashboard-account-card {
    max-width: 100%;
}

.dashboard-account-text {
    margin: 0 0 18px;

    line-height: 1.5;
}

.dashboard-account-action {
    width: 100%;
    max-width: 300px;
}

/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 1000px) {

    .dashboard-action-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 800px) {

    .dashboard-kpis {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }

    .dashboard-head {
        flex-direction: column;
        align-items: stretch;
    }

    .dashboard-head-action {
        width: 100%;
    }

    .dashboard-logout {
        width: 100%;
    }
}

@media (max-width: 600px) {

    .dashboard-page {
        padding-top: 5px;
    }

    .dashboard-card {
        padding: 18px;
    }

    .dashboard-head-info h1 {
        font-size: 25px;
    }

    .dashboard-kpis {
        grid-template-columns: 1fr;

        gap: 12px;
    }

    .dashboard-action-grid {
        grid-template-columns: 1fr;

        gap: 12px;
    }

    .dashboard-action {
        min-height: 0;
    }

    .dashboard-account-action {
        max-width: none;
    }
}

</style>

{% endblock %}
'''

# ------------------------------------------------------------
# GUARDAR
# ------------------------------------------------------------

ARCHIVO.write_text(
    HTML,
    encoding="utf-8"
)

print()
print("=" * 65)
print("DASHBOARD ORGANIZADO CORRECTAMENTE")
print("=" * 65)
print()
print(f"Copia de seguridad: {BACKUP}")
print()
print("Se reorganizó:")
print("- encabezado del docente")
print("- botón Cerrar sesión")
print("- cuatro indicadores")
print("- Acciones rápidas")
print("- tarjetas de Citas")
print("- tarjeta de Calendario")
print("- tarjeta de Notificaciones")
print("- tarjeta de Solicitudes")
print("- Mi cuenta")
print("- botones y enlaces")
print("- diseño responsive")
print()
print("No se modificaron rutas.")
print("No se modificaron consultas.")
print("No se modificaron permisos.")
print("No se modificó MySQL.")
print()