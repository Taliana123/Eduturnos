@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul

echo ================================================
echo       EDUTURNOS - ESTADO
 echo ================================================
echo.
where docker >nul 2>&1
if not errorlevel 1 (
  echo [Docker]
  docker info >nul 2>&1
  if errorlevel 1 (echo No disponible) else (echo Disponible)
  docker compose -f docker-compose.local.yml ps
)
echo.
echo [Servidor local]
powershell -NoProfile -Command "try { $r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/health -TimeoutSec 2; Write-Host ('HTTP '+$r.StatusCode+' '+$r.Content) } catch { Write-Host 'No responde en 127.0.0.1:5000' }"
echo.
pause
endlocal
