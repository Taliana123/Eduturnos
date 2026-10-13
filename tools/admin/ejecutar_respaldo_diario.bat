@echo off
setlocal
set "ROOT=%~dp0..\.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "PYEXE=%ROOT%\.venv\Scripts\python.exe"
set "SCRIPT=%ROOT%\tools\admin\respaldo.py"
set "LOG=%ROOT%\data\private\backups\respaldo_diario.log"

if not exist "%PYEXE%" (
  echo [ERROR] No existe el entorno .venv de EDUTURNOS.
  exit /b 1
)

if not exist "%ROOT%\data\private\backups" mkdir "%ROOT%\data\private\backups"
"%PYEXE%" "%SCRIPT%" >>"%LOG%" 2>&1
exit /b %ERRORLEVEL%