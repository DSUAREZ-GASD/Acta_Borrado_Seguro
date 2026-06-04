from flask import flash, redirect, render_template, url_for, request
from flask_login import login_required, current_user
from flask_babel import gettext as _# type: ignore
from . import usuarios
from app import db
from app.models import Usuario, Equipo, Estado_usuario, Rol
from .forms import FormRegistrarUsuario, FormRestablecerUsuario, FormPerfil, FormNuevaClave
from app.utils import reiniciar_intentos_usuario, acceso_requerido

# Ruta para crear un usuario
@usuarios.route('/crear', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def crear():
    usuario = Usuario()
    form_registrar = FormRegistrarUsuario()
    default_password = "GrupoASD123*"
    
    if form_registrar.validate_on_submit():
        try:
            form_registrar.populate_obj(usuario)
            
            string_rol_seleccionado = form_registrar.rol.data
            usuario.rol = next(e for e in Rol if e.value == string_rol_seleccionado)
            # Se establece la contraseña por defecto para nuevos usuarios
            usuario.set_password(default_password)
            db.session.add(usuario)
            db.session.commit()
            flash(_("Registro de usuario exitoso"), "success")
            return redirect(url_for('usuario.lista'))
        except Exception as e:
            db.session.rollback()
            flash(_("Error al crear usuario: {}").format(e), "error")
    
    form_registrar.password.data = default_password

    return render_template('usuario/crear.html', form=form_registrar)

# Ruta para ver la lista de usuarios
@usuarios.route('/lista')
@acceso_requerido(roles=["Administrador"])
@login_required
def lista():
    try:
        usuarios_data = Usuario.query.all()
        return render_template('usuario/lista.html', usuarios=usuarios_data)
    except Exception as e:
        flash(_("Error al obtener lista de usuarios: {}").format(e), "error")
        return redirect(url_for('equipo.lista_equipos'))
    
# Ruta para editar el perfil de un usuario logueado
# app/usuario/routes.py

@usuarios.route('/perfil', methods=['GET', 'POST']) # <-- Quitamos <usuario_id> de la URL
@acceso_requerido(roles=["Administrador", "Agente_1", "Agente_2", "Agente_3"])
@login_required
def perfil(): # <-- Ya no necesita recibir usuario_id como parámetro
    # Al usar current_user directamente, el programa se vuelve más seguro y limpio
    usuario = current_user 
    form_perfil = FormPerfil(obj=usuario)
    
    if form_perfil.validate_on_submit():
        try:
            # Verificar que la contraseña actual sea correcta
            if not usuario.check_password(form_perfil.current_password.data):
                flash(_("La contraseña actual no es correcta"), "error")
                return redirect(url_for('usuario.perfil'))
                
            elif form_perfil.password.data != form_perfil.confirm_password.data:
                flash(_("Las contraseñas no coinciden"), "error")
                return redirect(url_for('usuario.perfil'))
                
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
                    flash(_("Tus datos fueron modificados con éxito"), "success")
                else:
                    flash(_("No se realizaron cambios"), "info")
                    
        except Exception as e:
            db.session.rollback()
            flash(_("Error al modificar tus datos: {}").format(e), "error")
        
        # Redirección inteligente y segura según el rol del usuario logueado
        if usuario.rol.value == "Administrador":
            return redirect(url_for('equipo.lista_equipos'))
        else:
            return redirect(url_for('equipo.lista_equipos_agente'))
    
    # Al cargar por GET, rellenamos el formulario con los datos actuales
    if request.method == 'GET':
        form_perfil.email.data = usuario.email
        form_perfil.userName.data = usuario.userName

    return render_template('usuario/perfil.html', form=form_perfil, usuario=usuario)

# Ruta para restablecer un usuario     
@usuarios.route('/restablecer/<usuario_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def restablecer_usuario(usuario_id):  # <--- CAMBIADO AQUÍ PARA EVITAR EL ENDPOINT DUPLICADO
    usuario = Usuario.query.get_or_404(usuario_id) 
    form_restablecer = FormRestablecerUsuario(obj=usuario)
    default_password = "GrupoASD123*"
    
    if form_restablecer.validate_on_submit():
        try:
            form_restablecer.populate_obj(usuario)
            
            string_rol_seleccionado = form_restablecer.rol.data
            usuario.rol = next(e for e in Rol if e.value == string_rol_seleccionado)
            
            # Limpieza centralizada de intentos
            reiniciar_intentos_usuario(usuario.userName)
            
            usuario.set_password(default_password)  
            db.session.commit()
            flash(_(f"Usuario {usuario.userName} restaurado con éxito"), "success")
            return redirect(url_for('usuario.lista'))
        except Exception as e:
            db.session.rollback()
            flash(_(f"Error al restablecer el usuario: {usuario.userName}. {e}"), "error")
    
    form_restablecer.password.data = default_password
    return render_template('usuario/reset.html', form=form_restablecer, usuario=usuario)


@usuarios.route('/cambiar-clave/<usuario_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador","Agente_1", "Agente_2", "Agente_3"])
@login_required
def cambiar_clave(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    form_cambio = FormNuevaClave()
    
    if current_user.id != int(usuario_id):
        flash(_("No tienes permiso para editar este perfil"), "info")
        return redirect(url_for('auth.login'))
    
    if form_cambio.validate_on_submit():
        try:
            if not usuario.check_password(form_cambio.current_password.data):
                flash(_("La contraseña actual no es correcta"), "error")
                return redirect(url_for('usuario.cambiar_clave', usuario_id=usuario_id))
            elif form_cambio.password.data != form_cambio.confirm_password.data:
                flash(_("Las contraseñas no coinciden"), "error")
                return redirect(url_for('usuario.cambiar_clave', usuario_id=usuario_id))
            else:
                usuario.set_password(form_cambio.password.data)
                db.session.commit()
                
                # Al cambiar clave exitosamente, garantizamos remover bloqueos previos
                reiniciar_intentos_usuario(usuario.userName)
                
                flash(_("Cambio de clave exitoso"), "success")
                rol_actual = current_user.rol.value
                
                if rol_actual == "Administrador":
                    return redirect(url_for('equipo.lista_equipos'))
                elif "Agente" in rol_actual:
                    return redirect(url_for('equipo.lista_equipos_agente'))
                else:
                    return redirect(url_for('equipo.lista_equipos_auditor'))
        except Exception as e:
            db.session.rollback()
            flash(_(f"Error al cambiar la contraseña: {e}"), "error")
    
    return render_template('usuario/clave.html', form=form_cambio) 

    
# Ruta para eliminar un usuario    
@usuarios.route('/eliminar/<usuario_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def eliminar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    
    # Verificar si el usuario tiene equipos asignados
    equipos_asignados = Equipo.query.filter(Equipo.usuario_id == usuario.id).all()
    if equipos_asignados:
        flash(_("No se puede eliminar el usuario porque tiene equipos asignados"), "error")
        return redirect(url_for('usuario.lista'))
    
    try:
        db.session.delete(usuario)
        db.session.commit()
        flash(_(f"{usuario.userName} Eliminado"), "success")
    except Exception as e:
        db.session.rollback()
        flash(_("Error al eliminar el usuario: {}").format(e), "error")
     
    return redirect(url_for('usuario.lista'))
 
