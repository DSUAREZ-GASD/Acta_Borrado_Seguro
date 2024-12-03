import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel  # type: ignore
from .config import Config
from werkzeug.security import generate_password_hash
from datetime import datetime

#Crear los objetos de SQLAlchemy y Migrate
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

def crear_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = 'auth.login' # Redirigir a la página de login si no está autenticado
    babel = Babel(app)
    
    # Configuración de Babel
    app.config['BABEL_DEFAULT_LOCALE'] = 'es'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

    #blueprints
    from app.pdfs import pdf
    from app.equipos import equipos
    from app.usuarios import usuarios
    from app.auth import auth
    from app.representantes import representantes
    
    # Registrar blueprint
    app.register_blueprint(pdf)
    app.register_blueprint(equipos)
    app.register_blueprint(usuarios)
    app.register_blueprint(auth)
    app.register_blueprint(representantes)
    
    #traemos los modelos 
    with app.app_context():
        from .models import Equipo, Usuario, Representante, Jal, Consulta, Proceso, Estado_usuario, Rol
        db.create_all()
        init_admin_user()

    #Mensaje de seguridad para prevencion de ataques
    app.config["SECRET_KEY"] = Config.SECRET_KEY


    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))
    
    return app

# creacion de usuario por defecto
def init_admin_user():
    from .models import Usuario, Rol, Estado_usuario
    admin_user = Usuario.query.filter_by(userName='admin').first()
    if not admin_user:
        admin_user = Usuario(
            userName='admin', 
            email='admin@grupoasd.com', 
            rol=Rol.ADMINISTRADOR, 
            estado=Estado_usuario.ACTIVO, 
            password=generate_password_hash('GrupoASD123*'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(admin_user)
        db.session.commit()

# Crear directorio si no existe
def directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
app = crear_app()