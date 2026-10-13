$ErrorActionPreference = "Continue"
$root = "F:\edu_Final"
$python = "$root\.venv\Scripts\python.exe"
$network = Get-NetConnectionProfile -ErrorAction SilentlyContinue |
    Where-Object { $_.NetworkCategory -eq 'Private' } |
    Select-Object -First 1
$lanIp = if ($network) {
    Get-NetIPAddress -InterfaceIndex $network.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' } |
        Select-Object -First 1 -ExpandProperty IPAddress
}
if (-not $lanIp) {
    Write-Host "Configura la red de Windows como Privada para habilitar el acceso LAN seguro." -ForegroundColor Red
    exit 1
}
Set-Location $root
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "       EDUTURNOS - SERVIDOR ESTABLE" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
while ($true) {
    $puerto = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
    if ($puerto) {
        if ($puerto.LocalAddress -contains $lanIp) {
            Write-Host "EDUTURNOS ya esta disponible en la red privada." -ForegroundColor Green
            break
        }
        Write-Host "El puerto 5000 esta ocupado por un servidor que no escucha en la IP privada." -ForegroundColor Red
        exit 1
    }
    Write-Host "Iniciando Waitress..." -ForegroundColor Yellow
    & $python -m waitress "--listen=${lanIp}:5000" app:app
    Write-Host "Waitress se detuvo. Reiniciando en 2 segundos..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}
Write-Host ""
Write-Host "EDUTURNOS disponible en esta PC: http://${lanIp}:5000" -ForegroundColor Green
if ($lanIp) {
    Write-Host "En el celular (misma Wi-Fi): http://${lanIp}:5000" -ForegroundColor Green
}
