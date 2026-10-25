@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "ROOT=%~dp0.."
cd /d "%ROOT%"
chcp 65001 >nul 2>&1
set "LANIF="
set "LANIP="
for /f "delims=" %%I in ('powershell -NoProfile -Command "Get-NetConnectionProfile | Where-Object NetworkCategory -eq Private | Select-Object -First 1 -ExpandProperty InterfaceIndex"') do set "LANIF=%%I"
if not defined LANIF (
  echo [AVISO] La red no esta marcada como Privada; se usara igualmente la conexion activa con Internet.
  for /f "delims=" %%I in ('powershell -NoProfile -Command "Get-NetConnectionProfile | Where-Object IPv4Connectivity -eq Internet | Select-Object -First 1 -ExpandProperty InterfaceIndex"') do set "LANIF=%%I"
)
if not defined LANIF (
  echo [ERROR] No se encontro ninguna conexion de red activa.
  goto :fail
)
for /f "delims=" %%I in ('powershell -NoProfile -Command "Get-NetIPAddress -InterfaceIndex %LANIF% -AddressFamily IPv4 | Where-Object AddressState -eq Preferred | Select-Object -First 1 -ExpandProperty IPAddress"') do set "LANIP=%%I"
if not defined LANIP (
  echo [ERROR] No se encontro una direccion IPv4 en la red privada.
  goto :fail
)
set "LISTEN=%LANIP%:5000"
set "URL=http://%LANIP%:5000"
set "EDUTURNOS_BIND_IP=%LANIP%"
set "PYEXE=%ROOT%\.venv\Scripts\python.exe"
set "LOG=%ROOT%\eduturnos_server.log"
set "INSTALLLOG=%ROOT%\instalacion.log"

echo ============================================================
echo                 EDUTURNOS - INICIO RAPIDO
echo ============================================================

if exist "%PYEXE%" (
  "%PYEXE%" --version >nul 2>&1
  if not errorlevel 1 goto :venv_ok
  echo [ERROR] El entorno virtual existente no es valido.
  goto :fail
)

echo Preparando EDUTURNOS por primera vez...
set "PYTHON_CMD="
where py >nul 2>&1 && set "PYTHON_CMD=py"
if not defined PYTHON_CMD where python >nul 2>&1 && set "PYTHON_CMD=python"
if not defined PYTHON_CMD (
  echo [ERROR] No se encontro Python.
  goto :fail
)
%PYTHON_CMD% -m venv "%ROOT%\.venv" >nul 2>&1
if errorlevel 1 goto :fail

:venv_ok
if not exist "%ROOT%\.env" if exist "%ROOT%\.env.example" copy /y "%ROOT%\.env.example" "%ROOT%\.env" >nul
"%PYEXE%" -c "import flask,mysql.connector,waitress,dotenv" >nul 2>&1
if errorlevel 1 (
  echo Instalando dependencias por primera vez...
  "%PYEXE%" -m pip install -r "%ROOT%\requirements.txt" >"%INSTALLLOG%" 2>&1
  if errorlevel 1 goto :fail
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$svcs=Get-Service -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '(?i)mysql' -or $_.DisplayName -match '(?i)mysql' }; foreach($s in $svcs){ if($s.Status -ne 'Running'){ try { Start-Service -Name $s.Name -ErrorAction Stop } catch {} } }" >nul 2>&1

powershell -NoProfile -Command "try { $r=Invoke-WebRequest -UseBasicParsing '%URL%/health/live' -TimeoutSec 1; if($r.StatusCode -eq 200){exit 0} } catch {}; exit 1" >nul 2>&1
if not errorlevel 1 goto :check_db

if exist "%LOG%" del /q "%LOG%" >nul 2>&1
if defined EDUTURNOS_AUTOMATICO (
  start "" /b "%PYEXE%" -m waitress --listen=%LISTEN% wsgi:app >"%LOG%" 2>&1
) else (
  start "EDUTURNOS_SERVER" /min "%PYEXE%" -m waitress --listen=%LISTEN% wsgi:app >"%LOG%" 2>&1
)

powershell -NoProfile -Command "$deadline=(Get-Date).AddSeconds(10); while((Get-Date) -lt $deadline){ try { $r=Invoke-WebRequest -UseBasicParsing '%URL%/health/live' -TimeoutSec 1; if($r.StatusCode -eq 200){exit 0} } catch {}; Start-Sleep -Milliseconds 250 }; exit 1" >nul 2>&1
if errorlevel 1 goto :fail

:check_db
echo En el celular, usa http://%LANIP%:5000 en la misma Wi-Fi.
powershell -NoProfile -Command "try { $r=Invoke-WebRequest -UseBasicParsing '%URL%/health/ready' -TimeoutSec 2; if($r.StatusCode -eq 200){exit 0} } catch {}; exit 1" >nul 2>&1
if not errorlevel 1 (
  if not defined EDUTURNOS_AUTOMATICO start "" "%URL%"
  goto :done
)

where docker >nul 2>&1
if not errorlevel 1 (
  docker info >nul 2>&1
  if not errorlevel 1 (
    echo MySQL local no responde. Intentando levantar EDUTURNOS + MySQL con Docker...
    set "EDUTURNOS_BIND_IP=%LANIP%"
    docker compose -f "%ROOT%\docker-compose.local.yml" up -d --build >"%ROOT%\docker_local.log" 2>&1
    powershell -NoProfile -Command "$deadline=(Get-Date).AddSeconds(20); while((Get-Date) -lt $deadline){ try { $r=Invoke-WebRequest -UseBasicParsing '%URL%/health/ready' -TimeoutSec 1; if($r.StatusCode -eq 200){exit 0} } catch {}; Start-Sleep -Milliseconds 300 }; exit 1" >nul 2>&1
    if not errorlevel 1 (
      start "" "%URL%"
      goto :done
    )
  )
)

start "" "%URL%/estado"
echo EDUTURNOS no pudo conectar con una base de datos disponible.
echo Revisa %LOG%

goto :done

:fail
echo [ERROR] EDUTURNOS no pudo iniciar.
echo Revisa %LOG%
echo %INSTALLLOG%
if defined EDUTURNOS_AUTOMATICO goto :automatic_fail
pause
endlocal
exit /b 1

:automatic_fail
endlocal
exit /b 1

:done
endlocal
exit /b 0
