@echo off
setlocal
set "ROOT=%~dp0.."
cd /d "%ROOT%"
if not exist "venv\Scripts\python.exe" (
  echo Primero ejecuta PRIMERA_VEZ.bat
  pause
  exit /b 1
)
"venv\Scripts\python.exe" -m pip install -q -r requirements-dev.txt
if errorlevel 1 (
  echo No se pudieron preparar las dependencias de pruebas.
  pause
  exit /b 1
)
"venv\Scripts\python.exe" -m pytest -q
set ERR=%errorlevel%
echo.
if %ERR% EQU 0 (echo PRUEBAS EJECUTADAS CORRECTAMENTE.) else (echo HAY PRUEBAS CON FALLO. REVISA LA SALIDA.)
pause
endlocal & exit /b %ERR%
