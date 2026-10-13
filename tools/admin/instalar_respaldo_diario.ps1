$ErrorActionPreference = "Stop"
$scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Join-Path (Get-Location) "tools\admin" }
$root = (Resolve-Path (Join-Path $scriptRoot "..\..")).Path
$python = Join-Path $root ".venv\Scripts\python.exe"
$runner = Join-Path $scriptRoot "ejecutar_respaldo_diario.bat"

if (-not (Test-Path $python)) {
    throw "No existe el entorno Python .venv de EDUTURNOS en $root"
}

$taskName = "EDUTURNOS - Respaldo diario"
$runAt = (Get-Date).Date.AddHours(23)
$action = New-ScheduledTaskAction `
    -Execute $env:ComSpec `
    -Argument ('/d /c ""{0}""' -f $runner) `
    -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -Daily -At $runAt
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)
$principal = New-ScheduledTaskPrincipal `
    -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Respaldo íntegro de la base EDUTURNOS en data/private/backups." `
    -Force | Out-Null

Write-Host "Tarea instalada: $taskName, cada día a las 23:00."
Write-Host "Se ejecuta cuando la cuenta actual ha iniciado sesión."
Write-Host "Los archivos quedan en data/private/backups; verifica y prueba restauración periódicamente."