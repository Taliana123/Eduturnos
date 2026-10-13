@echo off
setlocal
cd /d "%~dp0.."
chcp 65001 >nul 2>&1

set "ROOT=%CD%"
set "WATCHER=%ROOT%\tools\supervisar_eduturnos.ps1"
set "TASK=EDUTURNOS - Servidor automatico"

if not exist "%WATCHER%" (
  echo [ERROR] No existe %WATCHER%
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ' + [char]34 + '%WATCHER%' + [char]34); $trigger=New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME; $settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1); $principal=New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited; Register-ScheduledTask -TaskName '%TASK%' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description 'Supervisa y reinicia EDUTURNOS cuando no responde.' -Force -ErrorAction Stop | Out-Null; Start-ScheduledTask -TaskName '%TASK%' -ErrorAction Stop"
if errorlevel 1 (
  echo.
  echo [ERROR] No se pudo registrar o iniciar la tarea automatica.
  exit /b 1
)

echo Tarea instalada: %TASK%
echo EDUTURNOS se verificara al iniciar sesion y cada minuto.
echo No cierres sesion ni apagues este equipo si necesitas acceso desde Internet.
endlocal
exit /b 0