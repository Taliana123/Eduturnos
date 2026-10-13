$ErrorActionPreference = "Stop"

$root = "F:\edu_Final"
$file = "$root\templates\solicitudes\index.html"

Write-Host "INICIANDO CORRECCION..."

if (!(Test-Path $file)) {
    Write-Host "NO EXISTE EL ARCHIVO:"
    Write-Host $file
    exit
}

# BACKUP
$backupDir = "$root\BACKUP_SOLICITUDES"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$backupFile = "$backupDir\index_backup.html"
Copy-Item $file $backupFile -Force

# LEER
$html = [System.IO.File]::ReadAllText(
    $file,
    [System.Text.Encoding]::UTF8
)

# ==================================================
# CORREGIR CARACTERES
# ==================================================

$html = $html.Replace("AtrÃ¡s", "&#8592; Atr&#225;s")
$html = $html.Replace("AtrÃƒÂ¡s", "&#8592; Atr&#225;s")

$html = $html.Replace("revisiÃ³n", "revisi&#243;n")
$html = $html.Replace("revisiÃƒÂ³n", "revisi&#243;n")

$html = $html.Replace("aparecerÃ¡", "aparecer&#225;")

$html = $html.Replace("ðŸ“‹", "&#128203;")

$html = $html.Replace("â†", "&#8592;")
$html = $html.Replace("â†’", "&#8594;")

# ==================================================
# CAMBIAR EL BOTON
# ==================================================

$html = $html.Replace(
    "+ Solicitar seguimiento",
    "+ Solicitar seguimiento"
)

# ==================================================
# AGREGAR CSS
# ==================================================

$css = @"

<style>

.solicitar-seguimiento-final {
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

"@

# ==================================================
# PONER CLASE AL ENLACE
# ==================================================

$buscar = '<a href="/solicitudes/nueva/docente">'
$reemplazar = '<a href="/solicitudes/nueva/docente" class="solicitar-seguimiento-final">'

$html = $html.Replace(
    $buscar,
    $reemplazar
)

# También por si el enlace tiene más atributos
$buscar2 = 'href="/solicitudes/nueva/docente"'
$reemplazar2 = 'href="/solicitudes/nueva/docente" class="solicitar-seguimiento-final"'

if ($html.Contains($buscar2) -and
    !$html.Contains('class="solicitar-seguimiento-final"')) {

    $html = $html.Replace(
        $buscar2,
        $reemplazar2
    )
}

# ==================================================
# INSERTAR CSS
# ==================================================

if (!$html.Contains("solicitar-seguimiento-final")) {

    $html = $html.Replace(
        "</body>",
        ($css + "</body>")
    )

}
else {

    if (!$html.Contains("<style>")) {
        $html = $html.Replace(
            "</body>",
            ($css + "</body>")
        )
    }
}

# ==================================================
# GUARDAR
# ==================================================

[System.IO.File]::WriteAllText(
    $file,
    $html,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host ""
Write-Host "======================================"
Write-Host " CORRECCION COMPLETADA"
Write-Host "======================================"
Write-Host ""
Write-Host "ARCHIVO:"
Write-Host $file
Write-Host ""
Write-Host "BACKUP:"
Write-Host $backupFile
Write-Host ""
Write-Host "LISTO."