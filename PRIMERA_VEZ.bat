@echo off
setlocal EnableExtensions
cd /d "%~dp0"
call "%~dp0tools\instalar_eduturnos.bat"
if errorlevel 1 exit /b 1
echo.
echo EDUTURNOS quedo preparado en este equipo.
echo Uso diario: doble clic en ABRIR_EDUTURNOS.vbs
echo Para administrar tareas tecnicas usa las opciones dentro de tools\admin.
pause
endlocal
