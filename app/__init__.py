from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

#blueprint
from app.pdfs import pdf
from app.equipos import equipos
from app.usuarios import usuarios
from app.auth import auth
from app.representantes import representantes

#Creación y configuración del app 
app = Flask(__name__)
app.config.from_object(Config)
b = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'auth.login' # Redirigir a la página de login si no está autenticado

#Crear los objetos de SQLAlchemy y Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#traemos los modelos 
from .models import Equipo, Usuario, Representante

#configurar y registrar blueprint
app.register_blueprint(pdf)
app.register_blueprint(equipos)
app.register_blueprint(usuarios)
app.register_blueprint(auth)
app.register_blueprint(representantes)

#Mensaje de seguridad para prevencion de ataques
app.config["SECRET_KEY"] = Config.SECRET_KEY


@app.route('/')
def home():
    return redirect('/auth/login')