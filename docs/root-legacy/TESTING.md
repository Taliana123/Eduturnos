# Pruebas EDUTURNOS

Instalar dependencias de desarrollo:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Ejecutar pruebas unitarias y de rutas:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Verificar conexión y tablas de MySQL:

```powershell
.\venv\Scripts\python.exe verify_installation.py
```
