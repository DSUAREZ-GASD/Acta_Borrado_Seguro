import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel 
from .config import Config

# 1. Definir objetos globales (sin inicializar)
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
babel = Babel()

def crear_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    
    # 2. Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    login.init_app(app)
    login.login_view = 'auth.login'
    login.login_message_category = 'warning' # Opcional: añade diseño Bootstrap a alertas de login
    
    # Configuración limpia de Babel
    app.config['BABEL_DEFAULT_LOCALE'] = 'es'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
    babel.init_app(app)

    # 3. Registrar Comandos de CLI ANTES de los Blueprints
    from app.commands import sync_pdf_configs
    app.cli.add_command(sync_pdf_configs)

    # 4. Blueprints (Importación interna para evitar ciclos)
    #from app.pdfs import pdf
    from app.equipo import equipos
    from app.usuario import usuarios as usuarios_bp
    from app.auth import auth
    from app.representante import representantes
    from app.acta_verificacion import acta_verificacion
    
    #app.register_blueprint(pdf)
    app.register_blueprint(equipos)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(auth)
    app.register_blueprint(representantes)
    app.register_blueprint(acta_verificacion)

    # ==============================================================================
    # 4.5 CONFIGURACIÓN DEL CARGADOR DE USUARIOS (FLASK-LOGIN)
    # ==============================================================================
    from .models import Usuario
    @login.user_loader
    def load_user(id):
        # Permite que current_user funcione correctamente en toda la aplicación
        return Usuario.query.get(int(id))

    # 5. Contexto de aplicación
    with app.app_context():
        from .models import (
            Equipo, Usuario, Representante, Proceso, 
            Estado_usuario, Rol, Actividad_verificacion, ActaConfig
        )
        db.create_all()
        init_admin_user()
        asegurar_directorios(app)

    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))
    
    return app

def init_admin_user():
    from .models import Usuario, Rol, Estado_usuario
    
    default_password = "GrupoASD123*"
    email_admin = "admin@grupoasd.com"
    
    try:
        # Verificamos si existe por username O por email único para evitar colisiones
        admin_user = Usuario.query.filter(
            (Usuario.userName == 'admin') | (Usuario.email == email_admin)
        ).first()
        
        if not admin_user:
            print("Iniciando creación del usuario administrador por defecto...")
            
            admin_user = Usuario(
                nombre="Administrador",
                apellido="Sistema",
                userName='admin', 
                email=email_admin, 
                rol=Rol.ADMINISTRADOR, 
                estado=Estado_usuario.ACTIVO
            )
            admin_user.set_password(default_password)
            
            db.session.add(admin_user)
            db.session.commit()
            print("Usuario administrador creado con éxito.")
        else:
            # Pailsafe de desarrollo: Nos aseguramos de que tenga asignado el Enum correcto
            if admin_user.rol != Rol.ADMINISTRADOR:
                admin_user.rol = Rol.ADMINISTRADOR
                db.session.commit()
                print("Rol del administrador sincronizado correctamente.")
                
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ Alerta no crítica en init_admin_user: {e}")

def asegurar_directorios(app):
    path_tmp = os.path.join(app.root_path, 'static', 'tmp')
    if not os.path.exists(path_tmp):
        os.makedirs(path_tmp)