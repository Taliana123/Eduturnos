from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parent

ARCHIVO = BASE / "templates" / "auth" / "registro.html"
BACKUP = BASE / "templates" / "auth" / "registro.html.backup_visual"

if not ARCHIVO.exists():
    print("[ERROR] No existe templates/auth/registro.html")
    raise SystemExit(1)

# Copia de seguridad
shutil.copy2(ARCHIVO, BACKUP)

HTML = r'''{% extends 'base.html' %}

{% block title %}Crear cuenta · EDUTURNOS{% endblock %}

{% block content %}

<section class="formulario ancho-medio registro-pagina">

    <div class="tarjeta form-card registro-contenedor">

        <div class="section-heading registro-encabezado">

            <span class="badge">Registro</span>

            <h1>Crear cuenta</h1>

            <p>
                Elige el tipo de registro. Esto no asigna el rol:
                el sistema lo valida contra la información institucional.
            </p>

        </div>

        <div class="registro-grid">

            {% for slug, info in portales.items() %}

            <article class="registro-opcion">

                <div class="registro-opcion-contenido">

                    <h3>
                        {{ info.label }}
                    </h3>

                    <p>
                        {{ info.descripcion }}
                    </p>

                </div>

                <a
                    class="boton boton-full registro-boton"
                    href="{{ url_for('auth.registro_portal', portal=slug) }}"
                >
                    Registrarme
                </a>

            </article>

            {% endfor %}

        </div>

        <div class="registro-volver">

            <a
                class="link-back"
                href="{{ url_for('auth.login') }}"
            >
                ← Volver a iniciar sesión
            </a>

        </div>

    </div>

</section>


<style>

    /* =====================================================
       EDUTURNOS - REGISTRO ORGANIZADO
       ===================================================== */

    .registro-pagina {
        width: 100%;
        padding: 20px 0;
    }

    /* Tarjeta exterior */

    .registro-contenedor {
        width: 100%;
        max-width: 1050px;
        margin: 0 auto;
        padding: 32px;
        box-sizing: border-box;
    }

    /* Encabezado */

    .registro-encabezado {
        width: 100%;
        margin: 0 0 28px 0;
        text-align: left;
    }

    .registro-encabezado h1 {
        margin: 0 0 10px 0;
        line-height: 1.2;
    }

    .registro-encabezado p {
        margin: 0;
        line-height: 1.55;
        max-width: 760px;
    }

    /* =====================================================
       CUADRÍCULA
       ===================================================== */

    .registro-grid {
        display: grid;

        grid-template-columns:
            repeat(3, minmax(0, 1fr));

        gap: 20px;

        width: 100%;

        margin: 0;
        padding: 0;

        align-items: stretch;

        box-sizing: border-box;
    }

    /* =====================================================
       TARJETAS DE OPCIONES
       ===================================================== */

    .registro-opcion {
        display: flex;

        flex-direction: column;

        justify-content: space-between;

        width: 100%;
        min-width: 0;

        min-height: 190px;

        margin: 0;
        padding: 22px;

        box-sizing: border-box;

        background: #ffffff;

        border: 1px solid #dbe3ec;
        border-radius: 12px;

        box-shadow:
            0 2px 7px rgba(15, 23, 42, 0.05);

        transition:
            transform 0.15s ease,
            box-shadow 0.2s ease,
            border-color 0.2s ease;
    }

    .registro-opcion:hover {
        transform: translateY(-2px);

        border-color: #c3d4ea;

        box-shadow:
            0 7px 18px rgba(15, 23, 42, 0.09);
    }

    /* Contenido superior */

    .registro-opcion-contenido {
        flex: 1;

        width: 100%;
        min-width: 0;
    }

    /* Títulos alineados */

    .registro-opcion h3 {
        width: 100%;

        min-height: 42px;

        margin: 0 0 10px 0;
        padding: 0;

        color: #0f172a;

        font-size: 18px;
        font-weight: 700;

        line-height: 1.25;
    }

    /* Descripciones alineadas */

    .registro-opcion p {
        width: 100%;

        min-height: 66px;

        margin: 0;

        color: #64748b;

        font-size: 14px;

        line-height: 1.5;
    }

    /* =====================================================
       BOTONES
       ===================================================== */

    .registro-boton {
        display: flex;

        align-items: center;
        justify-content: center;

        width: 100%;

        min-height: 46px;

        margin-top: 20px;

        box-sizing: border-box;

        text-align: center;

        text-decoration: none;
    }

    /* =====================================================
       VOLVER
       ===================================================== */

    .registro-volver {
        display: flex;

        align-items: center;

        justify-content: center;

        width: 100%;

        margin-top: 28px;
        padding-top: 22px;

        border-top: 1px solid #e2e8f0;
    }

    .registro-volver .link-back {
        display: inline-flex;

        align-items: center;

        text-decoration: none;
    }

    .registro-volver .link-back:hover {
        text-decoration: underline;
    }

    /* =====================================================
       TABLET
       ===================================================== */

    @media (max-width: 900px) {

        .registro-contenedor {
            max-width: 100%;
            padding: 26px;
        }

        .registro-grid {
            grid-template-columns:
                repeat(2, minmax(0, 1fr));
        }
    }

    /* =====================================================
       CELULAR
       ===================================================== */

    @media (max-width: 620px) {

        .registro-contenedor {
            padding: 20px;
        }

        .registro-grid {
            grid-template-columns: 1fr;

            gap: 16px;
        }

        .registro-opcion {
            min-height: 0;
        }

        .registro-opcion h3,
        .registro-opcion p {
            min-height: 0;
        }
    }

</style>

{% endblock %}
'''

ARCHIVO.write_text(
    HTML,
    encoding="utf-8"
)

print()
print("=" * 65)
print("REGISTRO ORGANIZADO CORRECTAMENTE")
print("=" * 65)
print()
print(f"Copia de seguridad: {BACKUP}")
print()
print("Se corrigió:")
print("- encabezado")
print("- distribución de las 5 opciones")
print("- tarjetas del mismo tamaño")
print("- títulos alineados")
print("- descripciones alineadas")
print("- botones alineados")
print("- enlace de volver")
print("- diseño responsive")
print("- caracteres dañados")
print()
print("No se modificó la base de datos.")
print("No se modificaron las rutas.")
print("No se modificaron los roles.")
print()