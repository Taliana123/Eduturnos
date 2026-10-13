@echo off
setlocal
cd /d "%~dp0"
where docker >nul 2>&1
if errorlevel 1 (echo Docker Desktop no está disponible.&pause&exit /b 1)
docker compose -f docker-compose.local.yml down
pause
