@echo off
setlocal
cd /d "%~dp0.."
chcp 65001 >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0admin\instalar_respaldo_diario.ps1"
if errorlevel 1 (
  echo [ERROR] No se pudo instalar el respaldo diario.
  pause
  exit /b 1
)
echo.
echo Instalacion del respaldo diario terminada.
pause
endlocal
exit /b 0