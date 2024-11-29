from flask import flash, redirect, render_template, url_for
from flask_login import login_required, current_user
from flask_babel import gettext as _
from . import usuarios
from app import db
from app.auth.routes import acceso_requerido
from app.models import Usuario,Equipo, Estado_usuario
from .forms import FormRegistrarUsuario, FormRestablecerUsuario, FormPerfil, FormNuevaClave

# Diccionario para almacenar y reiniciar los intentos fallidos de inicio de sesión
intentos_fallidos = {}

# Ruta para crear un usuario
@usuarios.route('/crear-usuario', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def crear_usuario():
    usuario = Usuario()
    form_registrar = FormRegistrarUsuario()
    default_password = "GrupoASD123*"
    
    if form_registrar.validate_on_submit():
        try:
            form_registrar.populate_obj(usuario)
            # Se establece la contraseña por defecto para nuevos usuarios
            usuario.set_password(default_password)
            db.session.add(usuario)
            db.session.commit()
            flash(_("Registro de usuario exitoso"), "success")
            return redirect(url_for('usuarios.lista_usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(_("Error al crear usuario: {}").format(e), "error")
    
    form_registrar.password.data = default_password

    return render_template('crear_usuario.html', form=form_registrar)

# Ruta para ver la lista de usuarios
@usuarios.route('/lista-usuarios')
@acceso_requerido(roles=["Administrador"])
@login_required
def lista_usuarios():
    try:
        usuarios = Usuario.query.all()
        return render_template('lista_usuarios.html', usuarios=usuarios)
    except Exception as e:
        flash(_("Error al obtener lista de usuarios: {}").format(e), "error")
        return redirect(url_for('equipos.listar'))
    
    
# Ruta para restablecer un usuario     
@usuarios.route('/restablecer-usuario/<usuario_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def restablecer_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id) 
    form_restablecer=FormRestablecerUsuario(obj = usuario)
    default_password = "GrupoASD123*"
    
    if form_restablecer.validate_on_submit():
        try:
            form_restablecer.populate_obj(usuario)
            if usuario.estado == Estado_usuario.INACTIVO:
                # Reiniciar contador de intentos fallidos
                intentos_fallidos[usuario.userName] = {'intentos': 0, 'ultimo_intento': None}
            usuario.set_password(default_password)  
            db.session.commit()
            flash(_(f"{usuario.userName} de usuario restaurado"), "success")
            return redirect(url_for('usuarios.lista_usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(_(f"Error al restablecer el usuario: {usuario.userName}").format(e), "error")
    
    form_restablecer.password.data = default_password
    
    return render_template('restablecer_usuario.html', form=form_restablecer, usuario=usuario)
    
# Ruta para eliminar un usuario    
@usuarios.route('/eliminar-usuario/<usuario_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def eliminar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    
    # Verificar si el usuario tiene equipos asignados
    equipos_asignados = Equipo.query.filter(Equipo.usuario_id == usuario.id).all()
    if equipos_asignados:
        flash(_("No se puede eliminar el usuario porque tiene equipos asignados"), "error")
        return redirect(url_for('usuarios.lista_usuarios'))
    
    try:
        db.session.delete(usuario)
        db.session.commit()
        flash(_(f"{usuario.userName} Eliminado"), "success")
    except Exception as e:
        db.session.rollback()
        flash(_("Error al eliminar el usuario: {}").format(e), "error")
     
    return redirect(url_for('usuarios.lista_usuarios'))
 
 
# Ruta para editar el perfil de un usuario logueado
@usuarios.route('/perfil/<usuario_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Agente"])
@login_required
def perfil(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id) 
    form_perfil = FormPerfil(obj = usuario)
    
    # Verificar si el usuario logueado es el mismo que el usuario a modificar
    if current_user.id != int(usuario_id):
        flash(_("No tienes permiso para editar este perfil"), "info")
        return redirect(url_for('equipos.lista_agente'))
    
    if form_perfil.validate_on_submit():
        try:
            # Verificar que la contraseña actual sea correcta
            if not usuario.check_password(form_perfil.current_password.data):
                flash(_("La contraseña actual no es correcta"), "error")
                return redirect (url_for('usuarios.perfil', usuario_id=usuario_id))
            elif form_perfil.password.data != form_perfil.confirm_password.data:
                flash(_("Las contraseñas no coinciden"), "error")
                return redirect (url_for('usuarios.perfil', usuario_id=usuario_id))
            else:
                cambios = False
                if form_perfil.password.data:
                    usuario.set_password(form_perfil.password.data)
                    cambios = True
                if form_perfil.email.data != usuario.email:
                    usuario.email = form_perfil.email.data
                    cambios = True
                if form_perfil.userName.data != usuario.userName:
                    usuario.userName = form_perfil.userName.data
                    cambios = True

                if cambios:    
                    db.session.commit()
                    flash(_("Tus datos fueron modificados con exito"), "success")
                else:
                    flash(_("No se realizaron cambios"), "info")
        except Exception as e:
            db.session.rollback()
            flash(_("Error al modificar tus datos: {}").format(e), "error")
        
        return redirect(url_for('equipos.lista_agente'))
    
    return render_template('perfil.html', form=form_perfil, usuario=usuario)
    
# Ruta para cambiar la contraseña de un usuario logueado
@usuarios.route('/cambiar-clave/<usuario_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador","Agente"])
@login_required
def cambiar_clave(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    form_cambio = FormNuevaClave()
    
    # Verificar si el usuario logueado es el mismo que el usuario a editar
    if current_user.id != int(usuario_id):
        flash(_("No tienes permiso para editar este perfil"), "info")
        return redirect(url_for('auth.login'))
    
    if form_cambio.validate_on_submit():
        try:
            if not usuario.check_password(form_cambio.current_password.data):
                flash(_("La contraseña actual no es correcta"), "error")
                return redirect (url_for('usuarios.cambiar_clave', usuario_id=usuario_id))
            elif form_cambio.password.data != form_cambio.confirm_password.data:
                flash(_("Las contraseñas no coinciden"), "error")
                return redirect (url_for('usuarios.cambiar_clave', usuario_id=usuario_id))
            else:
                usuario.set_password(form_cambio.password.data)
                db.session.commit()
                flash(_("Cambio de clave exitoso"), "success")
                if current_user.rol.value == "Administrador":
                    return redirect(url_for('equipos.lista_equipos'))
                elif current_user.rol.value == "Agente":
                    return redirect(url_for('equipos.lista_equipos_agente'))
                else:
                    flash(_("Error al cambiar la contraseña"), "error")
                    return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(_("Error al cambiar la contraseña: {}").format(e), "error")
    
    return render_template('cambiar_clave.html', form=form_cambio)