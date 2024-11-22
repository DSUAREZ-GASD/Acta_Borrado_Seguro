from datetime import datetime,timedelta
from functools import wraps

from flask import flash, render_template, redirect, url_for
from flask_login import login_user, logout_user, current_user,login_required

from app import db
from app.models import Usuario, Estado_usuario
from . import auth
from .forms import LoginForm

# Decorador para proteger rutas
def acceso_requerido(roles=None):
    """
    Decorador para proteger rutas y verificar roles de usuario.

    Args:
        roles (list): Lista de roles permitidos para acceder a la ruta.

    Returns:
        function: Función decorada que verifica autenticación y roles.
    """
    if roles is None:
        roles = []
        
    def decorador(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated is False:
                flash("Debes iniciar sesión para acceder a esta página")
                return redirect('/auth/login')
            if roles and current_user.rol.value not in roles:
                flash("No tienes permisos para acceder a esta página")
                return redirect('/auth/login')
            return f(*args, **kwargs)
        return decorated_function
    return decorador


MAX_INTENTOS = 5
BLOQUEO_TIEMPO = timedelta(minutes=15)

intentos_fallidos = {}

# Mensajes de error
MSG_USUARIO_NO_EXISTE = "No existe el usuario"
MSG_CUENTA_BLOQUEADA = "Tu cuenta ha sido bloqueada, contacta con el administrador"
MSG_CUENTA_BLOQUEADA_TEMP = "Tu cuenta ha sido bloqueada. Intenta más tarde"
MSG_CONTRASEÑA_INCORRECTA = "Contraseña incorrecta"
MSG_CAMBIAR_CONTRASEÑA = "Debes cambiar tu contraseña"
MSG_BIENVENIDO_EQUIPOS = "Bienvenido a Equipos"
MSG_USUARIO_SIN_ROL = "Tu usuario no tiene rol asignado"
MSG_ERROR = "Ocurrió un error: {}"
SESION_CERRADA = "Sesión cerrada"
MSG_ERROR_SESION = "Ocurrió al cerrar sesión: {}"

def verificar_intentos(u):
    intentos = intentos_fallidos.get(u.userName, {'intentos': 0, 'ultimo_intento': None})
    if intentos['intentos'] >= MAX_INTENTOS:
        tiempo_bloqueo = datetime.utcnow() - intentos['ultimo_intento']
        if tiempo_bloqueo < BLOQUEO_TIEMPO:
            flash(MSG_CUENTA_BLOQUEADA_TEMP)
            return False
        else:
            intentos_fallidos[u.userName] = {'intentos': 0, 'ultimo_intento': None}
    return True

def manejar_intento_fallido(u):
    intentos = intentos_fallidos.get(u.userName, {'intentos': 0, 'ultimo_intento': None})
    intentos['intentos'] += 1
    intentos['ultimo_intento'] = datetime.utcnow()
    intentos_fallidos[u.userName] = intentos

    if intentos['intentos'] >= MAX_INTENTOS:
        u.estado = Estado_usuario.INACTIVO
        db.session.commit()
        flash(MSG_CUENTA_BLOQUEADA_TEMP)
        return False
    else:
        flash(MSG_CONTRASEÑA_INCORRECTA)
        return True
    
def validar_usuario(u, password):
    if u is None:
        flash(MSG_USUARIO_NO_EXISTE)
        return False

    if u.estado.value == "Inactivo":
        flash(MSG_CUENTA_BLOQUEADA)
        return False

    if not verificar_intentos(u):
        return False

    if not u.check_password(password):
        if not manejar_intento_fallido(u):
            return False
        return False

    return True

def redirigir_por_rol(u):
    if u.rol.value == "Administrador":
        return redirect(url_for('equipos.lista_equipos'))
    elif u.rol.value == "Agente":
        return redirect(url_for('equipos.lista_equipos_agente'))
    else:
        flash(MSG_USUARIO_SIN_ROL)
        return redirect(url_for('auth.login'))

#ruta de login
@auth.route('/login', methods = ['GET','POST'])
def login():
    f = LoginForm()
    default_password = "GrupoASD123*"
    try:
        if f.validate_on_submit():
            u = Usuario.query.filter_by(userName=f.userName.data).first()
            
            if not validar_usuario(u, f.password.data):
                return redirect(url_for('auth.login'))
                 
            intentos_fallidos[u.userName] = {'intentos': 0, 'ultimo_intento': None}
            login_user(u,True)
            
            if f.password.data == default_password:
                flash(MSG_CAMBIAR_CONTRASEÑA)
                return redirect(url_for('usuarios.cambiar_clave', usuario_id=u.id))
            
            flash(MSG_BIENVENIDO_EQUIPOS)
            return redirigir_por_rol(u)
                
    except Exception as e:
        flash(MSG_ERROR.format(str(e)))
        return redirect(url_for('auth.login'))
 
    return render_template("login.html",f=f)


#ruta de logout
@auth.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash(SESION_CERRADA)
    except Exception as e:
        flash(MSG_ERROR_SESION.format(str(e)))
    return redirect(url_for('auth.login'))



