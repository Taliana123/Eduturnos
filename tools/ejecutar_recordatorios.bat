@echo off
setlocal
cd /d "%~dp0.."
chcp 65001 >nul 2>&1

set "PYEXE=%~dp0..\.venv\Scripts\python.exe"
if exist "%PYEXE%" goto run

where python >nul 2>&1
if not errorlevel 1 set "PYEXE=python"
if "%PYEXE%"=="" (
  echo [ERROR] No se encontro Python.
  exit /b 1
)

:run
"%PYEXE%" "%~dp0enviar_recordatorios.py"
set "RC=%ERRORLEVEL%"
endlocal & exit /b %RC%
