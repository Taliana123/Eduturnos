@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "ROOT=%~dp0.."
cd /d "%ROOT%"
chcp 65001 >nul 2>&1

 echo ==========================================
 echo   EDUTURNOS - INSTALACION UNICA
 echo ==========================================
set "PYTHON_CMD="
where py >nul 2>&1 && set "PYTHON_CMD=py"
if not defined PYTHON_CMD where python >nul 2>&1 && set "PYTHON_CMD=python"
if not defined PYTHON_CMD (
  echo No se encontro Python 3.13+.
  pause
  exit /b 1
)

if not exist "venv\Scripts\python.exe" (
  echo Creando entorno virtual...
  %PYTHON_CMD% -m venv venv
  if errorlevel 1 goto :error
) else (
  "venv\Scripts\python.exe" --version >nul 2>&1
  if errorlevel 1 (
    echo El entorno virtual no es valido. Se recreara...
    rmdir /s /q "venv"
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 goto :error
  )
)

if not exist ".env" if exist ".env.example" (
  copy /y ".env.example" ".env" >nul
  echo Se creo .env a partir de .env.example.
  echo Revisa las variables de MySQL antes de iniciar.
)

echo Instalando dependencias...
"venv\Scripts\python.exe" -m pip install -r requirements.txt >"instalacion.log" 2>&1
if errorlevel 1 goto :error

REM Dejar MySQL en inicio automatico si el servicio existe.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=Get-Service -ErrorAction SilentlyContinue | ? { $_.Name -match '(?i)mysql' -or $_.DisplayName -match '(?i)mysql' } | Select-Object -First 1; if($s){ try { Set-Service -Name $s.Name -StartupType Automatic -ErrorAction Stop } catch {}; if($s.Status -ne 'Running'){ try { Start-Service -Name $s.Name -ErrorAction Stop } catch {} } }" >nul 2>&1

echo.
echo ==========================================
echo   INSTALACION TERMINADA CORRECTAMENTE
echo ==========================================
echo.
echo Para abrir EDUTURNOS usa:
echo   ABRIR_EDUTURNOS.vbs
endlocal
exit /b 0

:error
echo.
echo Ocurrio un error durante la instalacion.
echo Revisa instalacion.log en la carpeta del proyecto.
pause
endlocal
exit /b 1
