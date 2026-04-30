from dotenv import load_dotenv
import os

# Determina la ruta base del proyecto para el .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env')) # Sube un nivel si el .env está en la raíz

class Config:
    # Si no encuentra la URI en el .env, usa un sqlite local por defecto para no crashear
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-super-secret')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'salt-default')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-key-default')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Evita advertencias de recursos
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    