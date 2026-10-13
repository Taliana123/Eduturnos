@echo off
schtasks /Delete /TN "EDUTURNOS - Recordatorios" /F
if errorlevel 1 echo No existia una tarea con ese nombre o no fue posible eliminarla.
if not errorlevel 1 echo Tarea de recordatorios eliminada.
pause
