@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul 2>&1

echo Cerrando EDUTURNOS...

where docker >nul 2>&1
if not errorlevel 1 (
    docker info >nul 2>&1
    if not errorlevel 1 (
        docker compose -f docker-compose.local.yml down >nul 2>&1
    )
)

taskkill /FI "WINDOWTITLE eq EDUTURNOS_SERVER" /T /F >nul 2>&1
if exist "eduturnos_server.lock" del /q "eduturnos_server.lock" >nul 2>&1

echo EDUTURNOS detenido.
endlocal
