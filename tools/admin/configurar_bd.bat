@echo off
setlocal
set "ROOT=%~dp0..\.."
cd /d "%ROOT%"
if not exist "venv\Scripts\python.exe" (echo Ejecuta PRIMERA_VEZ.bat primero.&pause&exit /b 1)
"venv\Scripts\python.exe" "tools\admin\setup_database.py"
set ERR=%errorlevel%
pause
endlocal & exit /b %ERR%
