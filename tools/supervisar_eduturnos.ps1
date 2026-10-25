$ErrorActionPreference = 'SilentlyContinue'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$launcher = Join-Path $root 'tools\iniciar_eduturnos.bat'

while ($true) {
    $network = Get-NetConnectionProfile |
        Where-Object { $_.NetworkCategory -eq 'Private' } |
        Select-Object -First 1
    if (-not $network) {
        $network = Get-NetConnectionProfile |
            Where-Object { $_.IPv4Connectivity -eq 'Internet' } |
            Select-Object -First 1
    }
    $lanIp = if ($network) {
        Get-NetIPAddress -InterfaceIndex $network.InterfaceIndex -AddressFamily IPv4 |
            Where-Object {
                $_.AddressState -eq 'Preferred' -and
                $_.IPAddress -notlike '127.*' -and
                $_.IPAddress -notlike '169.254.*'
            } |
            Select-Object -First 1 -ExpandProperty IPAddress
    }

    if ($lanIp) {
        $healthy = $false
        try {
            $response = Invoke-WebRequest -UseBasicParsing "http://${lanIp}:5000/health/live" -TimeoutSec 3
            $healthy = $response.StatusCode -eq 200
        } catch {
            $healthy = $false
        }

        if (-not $healthy) {
            $env:EDUTURNOS_AUTOMATICO = '1'
            try {
                Start-Process -FilePath $launcher -WorkingDirectory $root -WindowStyle Hidden
            } finally {
                Remove-Item Env:\EDUTURNOS_AUTOMATICO -ErrorAction SilentlyContinue
            }
            Start-Sleep -Seconds 30
        }
    }

    Start-Sleep -Seconds 60
}