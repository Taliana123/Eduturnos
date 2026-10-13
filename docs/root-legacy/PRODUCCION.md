# Despliegue en producción

El proyecto puede extraerse en cualquier carpeta de Windows; los scripts usan rutas relativas.

1. Crear el entorno virtual con Python 3.13.
2. Instalar `requirements.txt`.
3. Crear/configurar MySQL.
4. Definir las variables de entorno de `.env.example`.
5. Cargar el directorio institucional real en `directorio_institucional` antes de permitir registros del personal.
6. Ejecutar Waitress con `wsgi:app`.
7. Colocar HTTPS mediante un proxy/reverse proxy en producción.
