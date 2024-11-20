from . import usuarios
from flask import render_template,redirect,flash
from .forms import NuevoUsuario, EditUsuarioForm, PerfilUsuarioForm
import app
from app.auth.routes import acceso_requerido
from flask_login import login_required

@usuarios.route('/crear_usuario', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def crear_cliente():
    u = app.models.Usuario()
    form = NuevoUsuario()
    default_password = "GrupoASD123*"
    if form.validate_on_submit():
        form.populate_obj(u)
        # Contraseña por defecto no puede ser igual al nombre de usuario
        if u.userName.lower() == default_password.lower():
            flash("La contraseña no puede ser igual al nombre de usuario")
            return redirect('/usuarios/lista_usuario')
        
        # Establecer la contraseña por defecto si no se proporciona una
        if not form.password.data:
            u.set_password(default_password)
        else:
            u.set_password(form.password.data)
            
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
        # Contraseña por defecto no puede ser igual al nombre de usuario
        if u.userName.lower() == default_password.lower():
            flash("La contraseña no puede ser igual al nombre de usuario")
            return redirect('/usuarios/lista_usuario')
        
        # Establecer la contraseña por defecto si no se proporciona una
        if not form_edit.password.data:
            u.set_password(default_password)
        else:
            u.set_password(form_edit.password.data)
            
        app.db.session.commit()
        flash("Actualizacion de usuario exitosa")
        return redirect('/usuarios/lista_usuario')
    
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
    form_edit=PerfilUsuarioForm(obj = u)
    if form_edit.validate_on_submit():
        form_edit.populate_obj(u)
        u.set_password(form_edit.password.data)
        app.db.session.commit()
        flash("Actualizacion de usuario exitosa")
        return redirect('/equipos/lista_agente')
    
    return render_template('perfil_usuario.html',
                           form=form_edit, usuario=u)