@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist backups mkdir backups
where mysqldump >nul 2>&1
if errorlevel 1 (echo No se encontró mysqldump en PATH. Consulta docs\BACKUPS.md.&pause&exit /b 1)
set "STAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "STAMP=%STAMP: =0%"
set "OUT=backups\eduturnos_%STAMP%.sql"
set /p USER=Usuario MySQL [root]: 
if "%USER%"=="" set "USER=root"
mysqldump -h 127.0.0.1 -P 3306 -u "%USER%" -p eduturnos > "%OUT%"
if errorlevel 1 (echo Error creando el backup.&pause&exit /b 1)
echo Backup creado: %OUT%
pause
