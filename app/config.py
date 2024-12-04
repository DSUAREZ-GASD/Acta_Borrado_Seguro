from dotenv import load_dotenv  # type: ignore
import os

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    SESSION_COOKIE_SAMESITE = 'Lax' # Configurar SameSite para las cookies de sesión
    SESSION_COOKIE_SECURE = False # Configurar Secure para las cookies de sesión
    
    