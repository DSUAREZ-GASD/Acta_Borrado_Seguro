# ACTAS DE BORRADO SEGURO

**Autor: Daniel Suarez y Ludwing Gonzalez**
**Fecha: 2024-10-30**
**Versión: 1.0**

## INSTALACIÓN

Inicializar entorno virtual con el comando

    python -m venv .venv

Activar entorno virtual con el comando
 
    .venv\Scripts\activate
 
Instala las dependencias dentro del archivo requirements.txt
 
    pip install -r requirements.txt

**Migracion de base de datos** 

* Nombre para la base de datos: secure_deletion_records.

 
* Esto creará una carpeta llamada migrations/ en tu proyecto, que almacenará los scripts de migración:

    flask db init

* En caso que solicite ajuste de conexion a la base de datos tienes que dirijirte al archivo alembic.ini y insertar la conexion que se encuentra en el env, sin comillas en la parte final del archivo y luego ejecutar el comando de migrate:

    sqlalchemy.url = mysql+mysqlconnector://root@localhost:3306/secure_deletion_records
 
* Cada vez que realices un cambio en el modelo, debes generar un nuevo script de migración. Usa el siguiente comando para crear un script basado en los cambios detectados en los modelos:

    flask db migrate -m "mensaje de la migración"
 
* Comando que actualizará la base de datos aplicando los cambios definidos en el último script de migración.
 
    flask db upgrade
 
* Deshacer la última migración (si es necesario):
 
    flask db downgrade
 
**Ejecución**

Despligue programa usamos el comando para entorno de desarrollo: 

    flask run


Despligue de programa con el comando para servidor waitress:

    waitress-serve --port=8000

Nota: Cuando se realize el despligue del programa, se debe tener en cuenta que el servidor se ejecutará en el puerto 8000 con la ip del equipo donde se encuentra el proyecto. Por lo tanto, para acceder al programa se debe dirigir a la ip del equipo donde se encuentra el proyecto y el puerto 8000. Por ejemplo:

105.2.154.1:8000


## Despliegue 

El despliegue se te lanzara al login, ingresa el usuario por defecto admin y contraseña para poder acceder a la aplicacion es GrupoASD123*, despues de ingresar los datos de acceso, te llevara a actualizar la contraseña y luego a la pagina principal de la aplicacion.






