# app/auth/routes.py
from flask import flash, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required
from app import db
from app.models import Usuario, Estado_usuario, Rol
from . import auth
from .forms import LoginForm

# Importaciones desde el núcleo de seguridad neutral
from app.utils import (
    verificar_intentos_usuario, 
    registrar_intento_fallido, 
    reiniciar_intentos_usuario
)

MSG_USUARIO_NO_EXISTE = ("No existe el usuario", "error")
MSG_CUENTA_BLOQUEADA = ("Tu cuenta ha sido bloqueada, contacta con el administrador", "error")
MSG_CUENTA_BLOQUEADA_TEMP = ("Tu cuenta ha sido bloqueada. Intenta más tarde", "warning")
MSG_CONTRASEÑA_INCORRECTA = ("Contraseña incorrecta", "error")
MSG_CAMBIAR_CONTRASEÑA = ("Debes cambiar tu contraseña", "info")
MSG_BIENVENIDO_EQUIPOS = ("Bienvenido a Equipos", "success")
MSG_USUARIO_SIN_ROL = ("Tu usuario no tiene rol asignado o permitido", "error")
MSG_ERROR = ("Ocurrió un error: {}", "error")

def validar_usuario(u, password):
    if u is None:
        flash(*MSG_USUARIO_NO_EXISTE)
        return False

    if u.estado == Estado_usuario.INACTIVO or u.estado.value == "Inactivo":
        flash(*MSG_CUENTA_BLOQUEADA)
        return False

    if not verificar_intentos_usuario(u):
        flash(*MSG_CUENTA_BLOQUEADA_TEMP)
        return False

    if not u.check_password(password):
        if not registrar_intento_fallido(u):
            flash(*MSG_CUENTA_BLOQUEADA_TEMP)
        else:
            flash(*MSG_CONTRASEÑA_INCORRECTA)
        return False
    return True

def redirigir_por_rol(u):
    rol_actual = u.rol.value
    if rol_actual == Rol.ADMINISTRADOR.value:
        return redirect(url_for('equipo.lista_equipos'))
    elif rol_actual in [Rol.AGENTE_OPERADOR.value, Rol.AGENTE_SUPERVISOR.value]:
        return redirect(url_for('equipo.lista_equipos_agente'))
    elif rol_actual == Rol.AGENTE_AUDITOR.value:
        return redirect(url_for('equipo.lista_equipos_auditor'))
    else:
        flash(*MSG_USUARIO_SIN_ROL)
        return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    default_password = "GrupoASD123*"
    try:
        if form.validate_on_submit():
            u = Usuario.query.filter_by(userName=form.userName.data).first()
            if not validar_usuario(u, form.password.data):
                return redirect(url_for('auth.login'))
                 
            reiniciar_intentos_usuario(u.userName)
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
    logout_user()
    flash("Sesión cerrada", "success")
    return redirect(url_for('auth.login'))