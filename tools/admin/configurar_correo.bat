@echo off
setlocal
cd /d "%~dp0"
set "PY="
where py >nul 2>&1 && set "PY=py"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if not defined PY (
  echo No se encontro Python.
  pause
  exit /b 1
)
if exist "venv\Scripts\python.exe" (
  "venv\Scripts\python.exe" configurar_correo.py
) else (
  "%PY%" configurar_correo.py
)
pause
