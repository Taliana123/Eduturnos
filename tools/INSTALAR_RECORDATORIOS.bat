@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
chcp 65001 >nul 2>&1

echo ================================================
echo   EDUTURNOS - PROGRAMAR RECORDATORIOS
echo ================================================
set "WRAPPER=%~dp0ejecutar_recordatorios.bat"

if not exist "%WRAPPER%" (
  echo [ERROR] No existe %WRAPPER%
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$action=New-ScheduledTaskAction -Execute 'cmd.exe' -Argument ('/d /c ""' + '%WRAPPER%' + '""'); $trigger=New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650); Register-ScheduledTask -TaskName 'EDUTURNOS - Recordatorios' -Action $action -Trigger $trigger -Description 'Recordatorios independientes de EDUTURNOS cada 5 minutos.' -Force -ErrorAction Stop"
if errorlevel 1 (
  echo.
  echo [ERROR] No se pudo registrar la tarea programada.
  echo Prueba ejecutar este archivo con permisos suficientes o crea la tarea manualmente en el Programador de tareas de Windows.
  exit /b 1
)

echo.
echo Tarea registrada: EDUTURNOS - Recordatorios
echo Frecuencia: cada 5 minutos
echo El proceso se ejecuta fuera de Flask/Waitress.
endlocal
exit /b 0
