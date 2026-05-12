import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel 
from .config import Config
from werkzeug.security import generate_password_hash
from datetime import datetime

# 1. Definir objetos globales (sin inicializar)
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

def crear_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    
    # 2. Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = 'auth.login'
    
    babel = Babel(app)
    app.config['BABEL_DEFAULT_LOCALE'] = 'es'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

    # 3. Registrar Comandos de CLI ANTES de los Blueprints
    from app.commands import sync_pdf_configs
    app.cli.add_command(sync_pdf_configs)

    # 4. Blueprints (Importación interna para evitar círculos)
    from app.pdfs import pdf
    from app.equipos import equipos
    from app.usuarios import usuarios
    from app.auth import auth
    from app.representantes import representantes
    from app.acta_verificacion import acta_verificacion
    
    app.register_blueprint(pdf)
    app.register_blueprint(equipos)
    app.register_blueprint(usuarios)
    app.register_blueprint(auth)
    app.register_blueprint(representantes)
    app.register_blueprint(acta_verificacion)

    # 5. Contexto de aplicación
    with app.app_context():
        from .models import (
            Equipo, Usuario, Representante, Proceso, 
            Estado_usuario, Rol, Actividad_verificacion, ActaConfig
        )
        db.create_all()
        init_admin_user()
        asegurar_directorios(app) # Movido aquí adentro

    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))
    
    return app

def init_admin_user():
    from .models import Usuario, Rol, Estado_usuario
    admin_user = Usuario.query.filter_by(userName='admin').first()
    if not admin_user:
        admin_user = Usuario(
            nombre="Administrador",
            apellido="Sistema",
            userName='admin', 
            email='admin@grupoasd.com', 
            rol=Rol.ADMINISTRADOR, 
            estado=Estado_usuario.ACTIVO, 
            password=generate_password_hash('GrupoASD123*')
        )
        db.session.add(admin_user)
        db.session.commit()

def asegurar_directorios(app):
    path_tmp = os.path.join(app.root_path, 'static', 'tmp')
    if not os.path.exists(path_tmp):
        os.makedirs(path_tmp)