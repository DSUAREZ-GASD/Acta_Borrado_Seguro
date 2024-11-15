# Proyecto actas pruebas

**Autor: Daniel Suarez y Ludwing**
**Fecha: 2024-10-30**
**Versión: 1.0**

## Instalación

Inicializar entorno virtual con el comando

python -m venv .venv

Activar entorno virtual con el comando
 
.venv\Scripts\activate
 
Instala las dependencias dentro del archivo requirements.txt
 
pip install -r requirements.txt
 
Ahora crea una base de datos con el mismo nombre de la que se encuentra en el archivo config en este caso es flask_shopy_2687365.
 
Usando los comandos 
 
* Esto creará una carpeta llamada migrations/ en tu proyecto, que almacenará los scripts de migración:

    flask db init
 
Cada vez que realices un cambio en el modelo, debes generar un nuevo script de migración. Usa el siguiente comando para crear un script basado en los cambios detectados en los modelos:
 
    flask db migrate -m "Mensaje de confirmación"
 
* Comando que actualizará la base de datos aplicando los cambios definidos en el último script de migración.
 
    flask db upgrade
 
 
 * Deshacer la última migración (si es necesario):
 
    flask db downgrade
 
 
Para ejecutar programa usamos el comando 

flask run