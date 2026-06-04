# app/utils/seguridad.py
from datetime import datetime, timedelta
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.models import Estado_usuario
from app import db

MAX_INTENTOS = 5
BLOQUEO_TIEMPO = timedelta(minutes=15)
intentos_fallidos = {}

# DECORADOR MAESTRO CENTRALIZADO (Punto neutral)
def acceso_requerido(roles=None):
    if roles is None:
        roles = []
    def decorador(f):
        @wraps(f)  # Esto es vital para que Flask no confunda los endpoints internos
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debes iniciar sesión para acceder a esta página", "warning")
                return redirect(url_for('auth.login'))
            
            if roles and current_user.rol.value not in roles:
                flash("No tienes permisos para acceder a esta página", "error")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorador

def verificar_intentos_usuario(usuario):
    intentos = intentos_fallidos.get(usuario.userName, {'intentos': 0, 'ultimo_intento': None})
    if intentos['intentos'] >= MAX_INTENTOS:
        tiempo_bloqueo = datetime.utcnow() - intentos['ultimo_intento']
        if tiempo_bloqueo < BLOQUEO_TIEMPO:
            return False
        else:
            reiniciar_intentos_usuario(usuario.userName)
    return True

def registrar_intento_fallido(usuario):
    intentos = intentos_fallidos.get(usuario.userName, {'intentos': 0, 'ultimo_intento': None})
    intentos['intentos'] += 1
    intentos['ultimo_intento'] = datetime.utcnow()
    intentos_fallidos[usuario.userName] = intentos

    if intentos['intentos'] >= MAX_INTENTOS:
        usuario.estado = Estado_usuario.INACTIVO
        db.session.commit()
        return False
    return True

def reiniciar_intentos_usuario(username):
    if username in intentos_fallidos:
        intentos_fallidos[username] = {'intentos': 0, 'ultimo_intento': None}
        
def usuario_debe_bloquear_maestro(usuario, equipo):
    """
    Retorna True si el equipo es maestro y el usuario NO es Administrador.
    Si retorna True, significa que los campos críticos deben estar protegidos.
    """
    # Si el equipo no está marcado como maestro, nadie se bloquea
    if not equipo.es_maestro:
        return False
        
    # Si el equipo es maestro pero el usuario es Administrador, tiene libre acceso
    if usuario.rol.value == "Administrador":
        return False
        
    # En cualquier otro caso (Agente_1, Agente_2, Agente_3), se deben bloquear los campos
    return True