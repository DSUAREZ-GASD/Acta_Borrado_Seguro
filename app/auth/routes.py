from datetime import datetime, timedelta
from functools import wraps
from flask import flash, render_template, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import Usuario, Estado_usuario, Rol
from . import auth
from .forms import LoginForm

# ==========================================
# DECORADOR MAESTRO DE ACCESO
# ==========================================
def acceso_requerido(roles=None):
    """
    Decorador para proteger rutas verificando los nuevos strings del Enum de Roles.
    Ejemplo: @acceso_requerido(roles=["Administrador", "Agente_3"])
    """
    if roles is None:
        roles = []
        
    def decorador(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debes iniciar sesión para acceder a esta página", "warning")
                return redirect(url_for('auth.login'))
            
            # Sincronizado con current_user.rol.value ("Administrador", "Agente_1", etc.)
            if roles and current_user.rol.value not in roles:
                flash("No tienes permisos para acceder a esta página", "error")
                # Redirección segura para no dejar al usuario en un bucle de login
                return redirect(url_for('auth.login'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorador


# ==========================================
# CONTROL DE INTENTOS Y SEGURIDAD
# ==========================================
MAX_INTENTOS = 5
BLOQUEO_TIEMPO = timedelta(minutes=15)
intentos_fallidos = {}

# Mensajes del sistema (Manteniendo la estructura corporativa)
MSG_USUARIO_NO_EXISTE = ("No existe el usuario", "error")
MSG_CUENTA_BLOQUEADA = ("Tu cuenta ha sido bloqueada, contacta con el administrador", "error")
MSG_CUENTA_BLOQUEADA_TEMP = ("Tu cuenta ha sido bloqueada. Intenta más tarde", "warning")
MSG_CONTRASEÑA_INCORRECTA = ("Contraseña incorrecta", "error")
MSG_CAMBIAR_CONTRASEÑA = ("Debes cambiar tu contraseña", "info")
MSG_BIENVENIDO_EQUIPOS = ("Bienvenido a Equipos", "success")
MSG_USUARIO_SIN_ROL = ("Tu usuario no tiene rol asignado o permitido", "error")
MSG_ERROR = ("Ocurrió un error: {}", "error")
SESION_CERRADA = ("Sesión cerrada", "success")
MSG_ERROR_SESION = ("Ocurrió al cerrar sesión: {}", "error")


def verificar_intentos(u):
    intentos = intentos_fallidos.get(u.userName, {'intentos': 0, 'ultimo_intento': None})
    if intentos['intentos'] >= MAX_INTENTOS:
        # Se asume zona horaria UTC para consistencia con los modelos
        tiempo_bloqueo = datetime.utcnow() - intentos['ultimo_intento']
        if tiempo_bloqueo < BLOQUEO_TIEMPO:
            flash(*MSG_CUENTA_BLOQUEADA_TEMP)
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
        flash(*MSG_CUENTA_BLOQUEADA_TEMP)
        return False
    else:
        flash(*MSG_CONTRASEÑA_INCORRECTA)
        return True


def validar_usuario(u, password):
    if u is None:
        flash(*MSG_USUARIO_NO_EXISTE)
        return False

    if u.estado.value == "Inactivo":
        flash(*MSG_CUENTA_BLOQUEADA)
        return False

    if not verificar_intentos(u):
        return False

    if not u.check_password(password):
        if not manejar_intento_fallido(u):
            return False
        return False

    return True


# ==========================================
# ENRUTAMIENTO INTELIGENTE POR PERFIL
# ==========================================
def redirigir_por_rol(u):
    """
    Evalúa el string de rol asignado al usuario y lo despacha
    a la vista correspondiente de la aplicación.
    """
    rol_actual = u.rol.value

    if rol_actual == Rol.ADMINISTRADOR.value:
        return redirect(url_for('equipo.lista_equipos'))
        
    elif rol_actual in [Rol.AGENTE_OPERADOR.value, Rol.AGENTE_SUPERVISOR.value]:
        # El Agente 1 y Agente 2 comparten el flujo operativo estándar de equipos
        return redirect(url_for('equipo.lista_equipos_agente'))
        
    elif rol_actual == Rol.AGENTE_AUDITOR.value:
        # Despachamos al Agente 3 a su vista exclusiva de auditoría de hash y reportes
        return redirect(url_for('equipo.lista_equipos_auditor'))
        
    else:
        flash(*MSG_USUARIO_SIN_ROL)
        return redirect(url_for('auth.login'))


# ==========================================
# CONTROLADORES DE RUTA (LOGIN / LOGOUT)
# ==========================================
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    default_password = "GrupoASD123*"
    try:
        if form.validate_on_submit():
            u = Usuario.query.filter_by(userName=form.userName.data).first()
            
            if not validar_usuario(u, form.password.data):
                return redirect(url_for('auth.login'))
                 
            intentos_fallidos[u.userName] = {'intentos': 0, 'ultimo_intento': None}
            login_user(u, remember=True)
            
            if form.password.data == default_password:
                flash(*MSG_CAMBIAR_CONTRASEÑA)
                return redirect(url_for('usuario.cambiar_clave', usuario_id=u.id))
            
            flash(*MSG_BIENVENIDO_EQUIPOS)
            return redirigir_por_rol(u)
                
    except Exception as e:
        db.session.rollback()
        flash(MSG_ERROR[0].format(str(e)), MSG_ERROR[1])
        return redirect(url_for('auth.login'))
 
    return render_template("login.html", form=form)


@auth.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash(*SESION_CERRADA)
    except Exception as e:
        flash(MSG_ERROR_SESION[0].format(str(e)), MSG_ERROR_SESION[1])
    return redirect(url_for('auth.login'))