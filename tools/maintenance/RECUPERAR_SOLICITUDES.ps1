$ErrorActionPreference = "Stop"

$root = "F:\edu_Final"
$target = "$root\templates\solicitudes\index.html"

Write-Host ""
Write-Host "=============================================="
Write-Host " EDUTURNOS - RECUPERAR SOLICITUDES"
Write-Host "=============================================="
Write-Host ""

# =========================================================
# BACKUP DEL ARCHIVO ACTUAL
# =========================================================

$emergency = "$root\BACKUP_ANTES_RECUPERAR"
New-Item -ItemType Directory -Path $emergency -Force | Out-Null

$emergencyFile = "$emergency\index_actual.html"

Copy-Item `
    $target `
    $emergencyFile `
    -Force

Write-Host "Backup de seguridad creado."
Write-Host ""

# =========================================================
# BUSCAR COPIAS HTML EN TODOS LOS BACKUPS
# =========================================================

$folders = Get-ChildItem `
    $root `
    -Directory `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -like "BACKUP*"
    }

$candidates = @()

foreach ($folder in $folders) {

    $files = Get-ChildItem `
        $folder.FullName `
        -Recurse `
        -File `
        -Filter "*.html" `
        -ErrorAction SilentlyContinue

    foreach ($f in $files) {

        try {

            $text = [System.IO.File]::ReadAllText(
                $f.FullName,
                [System.Text.Encoding]::UTF8
            )

            $score = 0

            if ($text.Contains("<!DOCTYPE")) {
                $score += 10
            }

            if ($text.Contains("<html")) {
                $score += 10
            }

            if ($text.Contains("Solicitudes de cita")) {
                $score += 10
            }

            if ($text.Contains("/solicitudes/nueva/docente")) {
                $score += 10
            }

            if ($text.Contains("$ErrorActionPreference")) {
                $score -= 100
            }

            if ($text.Contains("$patronDescripcion")) {
                $score -= 100
            }

            if ($text.Contains("$regexBoton")) {
                $score -= 100
            }

            if ($text.Contains("EDUTURNOS-SOLICITUDES-FINAL")) {
                $score -= 50
            }

            $candidates += [PSCustomObject]@{
                File = $f.FullName
                Score = $score
                Date = $f.LastWriteTime
                Length = $f.Length
            }

        }
        catch {
        }
    }
}

# =========================================================
# MOSTRAR CANDIDATOS
# =========================================================

Write-Host "COPIAS ENCONTRADAS:"
Write-Host ""

$candidates |
    Sort-Object Score,Date -Descending |
    Select-Object -First 15 |
    Format-Table Score,Date,Length,File -AutoSize

Write-Host ""

# =========================================================
# ELEGIR LA COPIA LIMPIA
# =========================================================

$clean = $candidates |
    Where-Object {
        $_.Score -ge 30
    } |
    Sort-Object Score,Date -Descending |
    Select-Object -First 1

if ($null -eq $clean) {

    Write-Host "NO SE ENCONTRO UNA COPIA HTML LIMPIA."
    Write-Host ""
    Write-Host "NO SE MODIFICO EL ARCHIVO."
    Write-Host ""
    exit
}

Write-Host "COPIA SELECCIONADA:"
Write-Host $clean.File
Write-Host ""

# =========================================================
# RESTAURAR
# =========================================================

Copy-Item `
    $clean.File `
    $target `
    -Force

Write-Host "INDEX.HTML RESTAURADO."
Write-Host ""

# =========================================================
# LEER COPIA RESTAURADA
# =========================================================

$html = [System.IO.File]::ReadAllText(
    $target,
    [System.Text.Encoding]::UTF8
)

# =========================================================
# LIMPIAR RESTOS DE NUESTROS PARCHES ANTERIORES
# =========================================================

$html = [regex]::Replace(
    $html,
    '(?is)<style[^>]*id=["''][^"'']*(EDUTURNOS|solicitudes)[^"'']*["''][^>]*>.*?</style>',
    ""
)

$html = [regex]::Replace(
    $html,
    '(?is)<script[^>]*id=["''][^"'']*(EDUTURNOS|solicitudes)[^"'']*["''][^>]*>.*?</script>',
    ""
)

# =========================================================
# NUEVO CSS + JAVASCRIPT
# =========================================================

$fix = @'
<style id="eduturnos-solicitudes-definitivo">

.eduturnos-solicitudes-final {
    width: 100% !important;
}

.eduturnos-solicitudes-back {
    display: inline-block !important;
    margin-bottom: 18px !important;
}

.eduturnos-solicitudes-description {
    margin-top: 5px !important;
    margin-bottom: 24px !important;
}

.eduturnos-solicitudes-empty {
    width: 100% !important;
    text-align: center !important;
    padding: 30px 20px !important;
    box-sizing: border-box !important;
}

.eduturnos-solicitudes-icon {
    font-size: 32px !important;
    line-height: 1 !important;
    margin-bottom: 15px !important;
}

.eduturnos-solicitudes-follow {
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
}

</style>

<script id="eduturnos-solicitudes-definitivo-js">

(function () {

    "use strict";

    function fixText(text) {

        var replacements = {
            "\u00C3\u00A1": "\u00E1",
            "\u00C3\u00A9": "\u00E9",
            "\u00C3\u00AD": "\u00ED",
            "\u00C3\u00B3": "\u00F3",
            "\u00C3\u00BA": "\u00FA",
            "\u00C3\u00B1": "\u00F1",
            "\u00C2\u00B7": "\u00B7",
            "\u00E2\u0086\u0090": "\u2190",
            "\u00E2\u0086\u0092": "\u2192",
            "\u00E2\u0080\u00B9": "\u2039",
            "\u00E2\u0080\u00BA": "\u203A"
        };

        Object.keys(replacements).forEach(function (bad) {
            text = text.split(bad).join(replacements[bad]);
        });

        return text;
    }

    function run() {

        var walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null
        );

        var nodes = [];
        var node;

        while ((node = walker.nextNode())) {
            nodes.push(node);
        }

        nodes.forEach(function (n) {

            var value = fixText(n.nodeValue);

            if (value !== n.nodeValue) {
                n.nodeValue = value;
            }

        });

        var links = document.querySelectorAll("a");

        links.forEach(function (link) {

            var href = link.getAttribute("href") || "";

            var text = (link.textContent || "").trim();

            if (href.indexOf("/auth/dashboard") >= 0) {

                if (
                    text.indexOf("Atr") >= 0 ||
                    text.indexOf("\u2190") >= 0
                ) {

                    link.innerHTML = "&#8592; Atr&#225;s";

                    link.classList.add(
                        "eduturnos-solicitudes-back"
                    );

                }

            }

            if (
                href.indexOf("/solicitudes/nueva/docente") >= 0
            ) {

                link.innerHTML =
                    "+ Solicitar seguimiento";

                link.classList.add(
                    "eduturnos-solicitudes-follow"
                );

            }

        });

        var elements = document.querySelectorAll("body *");

        elements.forEach(function (element) {

            if (element.children.length !== 0) {
                return;
            }

            var text = (element.textContent || "").trim();

            if (
                text.indexOf("Flujo formal de solicitud") >= 0
            ) {

                element.innerHTML =
                    "Flujo formal de solicitud, revisi&#243;n, propuesta y confirmaci&#243;n.";

                element.classList.add(
                    "eduturnos-solicitudes-description"
                );

            }

            if (
                text.indexOf("Cuando se registre una solicitud") >= 0
            ) {

                element.innerHTML =
                    "Cuando se registre una solicitud, aparecer&#225; aqu&#237;.";

            }

            if (
                text.indexOf("No hay solicitudes") >= 0
            ) {

                element.innerHTML =
                    "No hay solicitudes";

            }

            if (
                text.indexOf("\u00F0") >= 0
            ) {

                element.innerHTML =
                    "&#128203;";

                element.classList.add(
                    "eduturnos-solicitudes-icon"
                );

            }

        });

    }

    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            run
        );

    }
    else {

        run();

    }

})();

</script>
'@

# =========================================================
# INSERTAR SOLO ANTES DE BODY
# =========================================================

if ($html.Contains("</body>")) {

    $html = $html.Replace(
        "</body>",
        $fix + "`r`n</body>"
    )

}
else {

    $html = $html + "`r`n" + $fix

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

Write-Host ""
Write-Host "=============================================="
Write-Host " SOLICITUDES RESTAURADAS Y CORREGIDAS"
Write-Host "=============================================="
Write-Host ""
Write-Host "ARCHIVO:"
Write-Host $target
Write-Host ""
Write-Host "COPIA USADA:"
Write-Host $clean.File
Write-Host ""
Write-Host "BACKUP DEL ARCHIVO ANTERIOR:"
Write-Host $emergencyFile
Write-Host ""
Write-Host "TERMINADO."