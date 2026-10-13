@echo off
setlocal
set "ROOT=%~dp0.."
cd /d "%ROOT%"
set "LANIF="
set "LANIP="
for /f "delims=" %%I in ('powershell -NoProfile -Command "Get-NetConnectionProfile ^| Where-Object NetworkCategory -eq Private ^| Select-Object -First 1 -ExpandProperty InterfaceIndex"') do set "LANIF=%%I"
if not defined LANIF (echo Configura la red de Windows como Privada para habilitar acceso LAN seguro.&exit /b 1)
for /f "delims=" %%I in ('powershell -NoProfile -Command "Get-NetIPAddress -InterfaceIndex %LANIF% -AddressFamily IPv4 ^| Where-Object AddressState -eq Preferred ^| Select-Object -First 1 -ExpandProperty IPAddress"') do set "LANIP=%%I"
if not defined LANIP (echo No se encontro una direccion IPv4 en la red privada.&exit /b 1)
set "EDUTURNOS_BIND_IP=%LANIP%"
where docker >nul 2>&1
if errorlevel 1 (echo Docker Desktop no está instalado o no está en PATH.&pause&exit /b 1)
docker compose -f docker-compose.local.yml up -d
if errorlevel 1 (echo No se pudo iniciar el entorno Docker.&pause&exit /b 1)
echo En el celular, usa http://%LANIP%:5000 en la misma Wi-Fi.
start "" "http://%LANIP%:5000"
