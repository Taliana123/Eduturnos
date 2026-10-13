$ErrorActionPreference = "Stop"

$root = "F:\edu_Final"

$source = "$root\backup_listas_vacias_seguro\solicitudes\index.html"

$target = "$root\templates\solicitudes\index.html"

$backupDir = "$root\BACKUP_SOLICITUDES_FINAL"

Write-Host ""
Write-Host "=============================================="
Write-Host " EDUTURNOS - FIX SOLICITUDES"
Write-Host "=============================================="
Write-Host ""

if (!(Test-Path $source)) {
    Write-Host "ERROR: no existe la copia limpia:"
    Write-Host $source
    exit
}

if (!(Test-Path $target)) {
    Write-Host "ERROR: no existe el archivo:"
    Write-Host $target
    exit
}

# =========================================================
# BACKUP
# =========================================================

New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$fecha = Get-Date -Format "yyyyMMdd_HHmmss"

$backupFile = "$backupDir\index_$fecha.html"

Copy-Item $target $backupFile -Force

Write-Host "Backup creado."
Write-Host ""

# =========================================================
# RESTAURAR COPIA HTML LIMPIA
# =========================================================

Copy-Item $source $target -Force

Write-Host "Plantilla HTML limpia restaurada."
Write-Host ""

# =========================================================
# LEER HTML
# =========================================================

$html = [System.IO.File]::ReadAllText(
    $target,
    [System.Text.Encoding]::UTF8
)

# =========================================================
# CORREGIR CARACTERES DAÑADOS
# =========================================================

$html = $html.Replace("AtrÃ¡s", "Atr&#225;s")
$html = $html.Replace("revisiÃ³n", "revisi&#243;n")
$html = $html.Replace("aparecerÃ¡", "aparecer&#225;")
$html = $html.Replace("aquÃ­", "aqu&#237;")
$html = $html.Replace("confirmaciÃ³n", "confirmaci&#243;n")

$html = $html.Replace("â†", "&#8592;")
$html = $html.Replace("â†’", "&#8594;")

# =========================================================
# CSS
# =========================================================

$css = @"
<style id="EDUTURNOS_SOLICITUDES_CSS_FINAL">

.solicitudes-final-contenedor {
    width: 100%;
}

.solicitudes-final-atras {
    display: inline-block;
    margin-bottom: 18px;
    text-decoration: none !important;
}

.solicitudes-final-descripcion {
    margin-top: 6px !important;
    margin-bottom: 24px !important;
}

.solicitudes-final-vacio {
    width: 100% !important;
    text-align: center !important;
    padding: 32px 20px !important;
    box-sizing: border-box !important;
}

.solicitudes-final-icono {
    font-size: 32px !important;
    line-height: 1 !important;
    margin-bottom: 14px !important;
}

.solicitudes-final-vacio h2 {
    margin-bottom: 8px !important;
}

.solicitudes-final-vacio p {
    margin-bottom: 22px !important;
}

a.solicitudes-final-seguimiento {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: auto !important;
    min-width: 0 !important;
    min-height: 40px !important;
    padding: 9px 16px !important;
    font-size: 15px !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
    text-decoration: none !important;
    box-sizing: border-box !important;
}

</style>
"@

# =========================================================
# JAVASCRIPT
# =========================================================

$js = @"
<script id="EDUTURNOS_SOLICITUDES_JS_FINAL">

document.addEventListener("DOMContentLoaded", function () {

    var zona = document.querySelector(".pagina-contenido");

    if (!zona) {
        return;
    }

    /* -------------------------------------------------
       CORREGIR TEXTO DAÑADO
       ------------------------------------------------- */

    var walker = document.createTreeWalker(
        zona,
        NodeFilter.SHOW_TEXT,
        null
    );

    var nodos = [];
    var nodo;

    while ((nodo = walker.nextNode())) {
        nodos.push(nodo);
    }

    nodos.forEach(function (n) {

        var texto = n.nodeValue;

        texto = texto.split("AtrÃ¡s").join("Atrás");
        texto = texto.split("revisiÃ³n").join("revisión");
        texto = texto.split("aparecerÃ¡").join("aparecerá");
        texto = texto.split("aquÃ­").join("aquí");
        texto = texto.split("confirmaciÃ³n").join("confirmación");
        texto = texto.split("â†").join("←");
        texto = texto.split("â†’").join("→");

        n.nodeValue = texto;
    });

    /* -------------------------------------------------
       ATRAS
       ------------------------------------------------- */

    var enlaces = zona.querySelectorAll("a");

    enlaces.forEach(function (enlace) {

        var href = enlace.getAttribute("href") || "";
        var texto = (enlace.textContent || "").trim();

        if (
            href.indexOf("dashboard") >= 0 &&
            (
                texto.indexOf("Atr") >= 0 ||
                texto.indexOf("←") >= 0
            )
        ) {
            enlace.innerHTML = "← Atrás";
            enlace.classList.add("solicitudes-final-atras");
        }

        /* ---------------------------------------------
           BOTON SEGUIMIENTO
           --------------------------------------------- */

        if (
            href.indexOf("/solicitudes/nueva/docente") >= 0
        ) {
            enlace.textContent = "+ Solicitar seguimiento";
            enlace.classList.add(
                "solicitudes-final-seguimiento"
            );
        }
    });

    /* -------------------------------------------------
       DESCRIPCION
       ------------------------------------------------- */

    var elementos = zona.querySelectorAll("*");

    elementos.forEach(function (elemento) {

        if (elemento.children.length !== 0) {
            return;
        }

        var texto = (elemento.textContent || "").trim();

        if (
            texto.indexOf("Flujo formal de solicitud") >= 0
        ) {
            elemento.textContent =
                "Flujo formal de solicitud, revisión, propuesta y confirmación.";

            elemento.classList.add(
                "solicitudes-final-descripcion"
            );
        }

        if (
            texto.indexOf("Cuando se registre una solicitud") >= 0
        ) {
            elemento.textContent =
                "Cuando se registre una solicitud, aparecerá aquí.";
        }

        if (
            texto === "No hay solicitudes"
        ) {
            elemento.textContent =
                "No hay solicitudes";
        }

    });

    /* -------------------------------------------------
       ICONO
       ------------------------------------------------- */

    elementos.forEach(function (elemento) {

        if (elemento.children.length !== 0) {
            return;
        }

        var texto = (elemento.textContent || "").trim();

        if (
            texto.indexOf("ð") === 0 ||
            texto.indexOf("📋") === 0
        ) {
            elemento.textContent = "📋";
            elemento.classList.add(
                "solicitudes-final-icono"
            );
        }

    });

});

</script>
"@

# =========================================================
# QUITAR VERSIONES ANTERIORES DE NUESTRO FIX
# =========================================================

$inicioCss = $html.IndexOf(
    '<style id="EDUTURNOS_SOLICITUDES_CSS_FINAL">'
)

if ($inicioCss -ge 0) {

    $finCss = $html.IndexOf(
        "</style>",
        $inicioCss
    )

    if ($finCss -ge 0) {

        $finCss = $finCss + 8

        $html = $html.Remove(
            $inicioCss,
            $finCss - $inicioCss
        )
    }
}

$inicioJs = $html.IndexOf(
    '<script id="EDUTURNOS_SOLICITUDES_JS_FINAL">'
)

if ($inicioJs -ge 0) {

    $finJs = $html.IndexOf(
        "</script>",
        $inicioJs
    )

    if ($finJs -ge 0) {

        $finJs = $finJs + 9

        $html = $html.Remove(
            $inicioJs,
            $finJs - $inicioJs
        )
    }
}

# =========================================================
# INSERTAR CSS Y JS
# =========================================================

$insertar = $css + "`r`n" + $js

$posEndBlock = $html.LastIndexOf(
    "{% endblock %}"
)

if ($posEndBlock -ge 0) {

    $html = $html.Insert(
        $posEndBlock,
        $insertar + "`r`n"
    )

}
else {

    $html = $html + "`r`n" + $insertar

}

# =========================================================
# GUARDAR
# =========================================================

$utf8 = New-Object System.Text.UTF8Encoding($false)

[System.IO.File]::WriteAllText(
    $target,
    $html,
    $utf8
)

# =========================================================
# VERIFICAR
# =========================================================

$final = [System.IO.File]::ReadAllText(
    $target,
    [System.Text.Encoding]::UTF8
)

Write-Host ""
Write-Host "=============================================="
Write-Host " VERIFICACION"
Write-Host "=============================================="
Write-Host ""

if ($final.Contains("$ErrorActionPreference")) {
    Write-Host "ERROR: PowerShell encontrado dentro del HTML."
}
else {
    Write-Host "OK: HTML limpio."
}

if ($final.Contains("Solicitudes de cita")) {
    Write-Host "OK: titulo encontrado."
}
else {
    Write-Host "ERROR: titulo no encontrado."
}

if ($final.Contains("Solicitar seguimiento")) {
    Write-Host "OK: boton encontrado."
}
else {
    Write-Host "ERROR: boton no encontrado."
}

if ($final.Contains("/solicitudes/nueva/docente")) {
    Write-Host "OK: enlace conservado."
}
else {
    Write-Host "ERROR: enlace no encontrado."
}

if ($final.Contains("EDUTURNOS_SOLICITUDES_CSS_FINAL")) {
    Write-Host "OK: CSS agregado."
}
else {
    Write-Host "ERROR: CSS no agregado."
}

if ($final.Contains("EDUTURNOS_SOLICITUDES_JS_FINAL")) {
    Write-Host "OK: JavaScript agregado."
}
else {
    Write-Host "ERROR: JavaScript no agregado."
}

Write-Host ""
Write-Host "=============================================="
Write-Host " CORRECCION TERMINADA"
Write-Host "=============================================="
Write-Host ""
Write-Host "Archivo:"
Write-Host $target
Write-Host ""
Write-Host "Backup:"
Write-Host $backupFile
Write-Host ""