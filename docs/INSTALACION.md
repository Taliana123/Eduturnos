# Instalación EDUTURNOS

## 1. Preparar Python
```powershell
# Abre PowerShell en la carpeta del proyecto.
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 2. Configurar MySQL
```powershell
venv\Scripts\python.exe setup_database.py
venv\Scripts\python.exe test_db.py
```

## 3. Datos de prueba opcionales
```powershell
venv\Scripts\python.exe seed.py
```
Solo para desarrollo local: las credenciales creadas por `seed.py` son de prueba y no deben utilizarse en producción.

## 4. Abrir EDUTURNOS
```powershell
venv\Scripts\python.exe app.py
```
Abrir `http://127.0.0.1:5000`.

## 5. Producción
Usar `wsgi:app` con Waitress y variables de entorno. Nunca publicar la contraseña de MySQL ni las credenciales SMTP en el repositorio.
