from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_babel import Babel
from .config import Config

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
    Bootstrap(app)
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
        from .models import Equipo, Usuario, Representante
        db.create_all()

    #Mensaje de seguridad para prevencion de ataques
    app.config["SECRET_KEY"] = Config.SECRET_KEY


    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))
    
    return app

app = crear_app()