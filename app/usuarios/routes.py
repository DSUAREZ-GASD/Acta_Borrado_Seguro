from . import usuarios
from flask import render_template,redirect,flash
from .forms import NuevoUsuario, EditUsuarioForm, PerfilUsuarioForm, CambiarPasswordForm
import app
from app.auth.routes import acceso_requerido
from flask_login import current_user, login_required

intentos_fallidos = {}
@usuarios.route('/crear_usuario', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def crear_cliente():
    u = app.models.Usuario()
    form = NuevoUsuario()
    default_password = "GrupoASD123*"
    if form.validate_on_submit():
        form.populate_obj(u)
        # Establecer la contraseña por defecto si no se proporciona una
        u.set_password(default_password)
        app.db.session.add(u)
        app.db.session.commit()
        flash("Registro de usuario exitoso")
        return redirect('/usuarios/lista_usuario')
    
    form.password.data = default_password

    return render_template('nuevo_usuario.html', form=form)


@usuarios.route('/lista_usuario')
@acceso_requerido(roles=["Administrador"])
@login_required
def listar():
    usuarios = app.Usuario.query.all()

    return render_template('lista_usuarios.html',
                           usuarios=usuarios)
    
      
@usuarios.route('/editar_usuario/<usuario_id>',
                methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def editar(usuario_id):
    u = app.models.Usuario.query.get(usuario_id) 
    form_edit=EditUsuarioForm(obj = u)
    default_password = "GrupoASD123*"
    if form_edit.validate_on_submit():
        form_edit.populate_obj(u)
        if u.estado == app.models.Estado_usuario.INACTIVO:
            # Reiniciar contador de intentos fallidos
            intentos_fallidos[u.userName] = {'intentos': 0, 'ultimo_intento': None}
        u.set_password(default_password)  
        app.db.session.commit()
        flash("Actualizacion de usuario exitosa")
        return redirect('/usuarios/lista_usuario')
    
    form_edit.password.data = default_password
    
    return render_template('editar_usuario.html',
                           form=form_edit, usuario=u)
    
    
@usuarios.route('/eliminar_usuario/<usuario_id>',
                methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def eliminar(usuario_id):
     u = app.models.Usuario.query.get(usuario_id)
     app.db.session.delete(u)
     app.db.session.commit()
     flash("Usuario Eliminado")
     return redirect('/usuarios/lista_usuario')
 
 
# Ruta para editar el perfil de un usuario logueado
@usuarios.route('/perfil/<usuario_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Agente"])
@login_required
def editar_perfil(usuario_id):
    
    u = app.models.Usuario.query.get(usuario_id) 
    form_modificar=PerfilUsuarioForm(obj = u)
    
    # Verificar si el usuario logueado es el mismo que el usuario a editar
    if current_user.id != int(usuario_id):
        flash("No tienes permiso para editar este perfil")
        return redirect('/equipos/lista_agente')
    
    if form_modificar.validate_on_submit():
        # Verificar que la contraseña actual sea correcta
        if not u.check_password(form_modificar.current_password.data):
            flash("La contraseña actual no es correcta")
            return redirect (f'/usuarios/perfil/{usuario_id}')
        elif form_modificar.password.data != form_modificar.confirm_password.data:
            flash("Las contraseñas no coinciden")
            return redirect (f'/usuarios/perfil/{usuario_id}')
        else:
            if form_modificar.password.data:
                u.set_password(form_modificar.password.data)           
        form_modificar.populate_obj(u)
        u.set_password(form_modificar.password.data)
        app.db.session.commit()
        flash("Actualizacion de usuario exitosa")
        return redirect('/equipos/lista_agente')
    
    return render_template('perfil_usuario.html',
                           form=form_modificar, usuario=u)
    
# Ruta para cambiar la contraseña de un usuario logueado
@usuarios.route('/cambiar_contraseña/<usuario_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador","Agente"])
@login_required
def cambiar_contraseña(usuario_id):
    u = app.models.Usuario.query.get(usuario_id)
    form_cambio = CambiarPasswordForm()
    
    # Verificar si el usuario logueado es el mismo que el usuario a editar
    if current_user.id != int(usuario_id):
        flash("No tienes permiso para editar este perfil")
        return redirect('/auth/login')
    
    if form_cambio.validate_on_submit():
        if not u.check_password(form_cambio.current_password.data):
            flash("La contraseña actual no es correcta")
            return redirect (f'/usuarios/cambiar_contraseña/{usuario_id}')
        elif form_cambio.password.data != form_cambio.confirm_password.data:
            flash("Las contraseñas no coinciden")
            return redirect (f'/usuarios/cambiar_contraseña/{usuario_id}')
        else:
            u.set_password(form_cambio.password.data)
            app.db.session.commit()
            if current_user.rol.value == "Administrador":
                flash("Registro de equipo exitoso")
                return redirect('/equipos/listar')
            elif current_user.rol.value == "Agente":
                flash("Registro de equipo exitoso")
                return redirect('/equipos/lista_agente')
            else:
                flash("Error al registrar equipo")
    
    return render_template('cambiar_clave.html', form=form_cambio)