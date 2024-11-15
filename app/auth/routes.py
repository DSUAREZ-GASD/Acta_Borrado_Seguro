from . import auth
#el . es para que nos importe todo el modulo
from flask import render_template, redirect, flash
from .forms import LoginForm
import app
#se llama al modelo

#dependecias de autenticacion
from flask_login import current_user,login_user,logout_user 
#para comprobar al usuario actual

#ruta de login
@auth.route('/login', methods = ['GET','POST'])
def login():
    f = LoginForm()
    try:
        if f.validate_on_submit():
            c = app.models.Usuario.query.filter_by(userName=f.userName.data).first()
            if c is None:
                print("Usuario no existe")
                flash("No exite el usuario")
                return redirect('/auth/login')
            if c.check_password(f.password.data) is False:
                print("la contraseña es erronea")
                flash("clave errónea")
                return redirect('/auth/login')
            
            login_user(c,True)
            print("Acesso al programa")
            flash("Bienvenido a Equipos")
            return redirect('/equipos/listar')
    except Exception as e:
        flash(f"Ocurrió un error: {e}")
        return redirect('/auth/login')
 
    return render_template("login.html",f=f)


#ruta de logout
@auth.route('/logout')
def logout():
    logout_user()
    flash("sesión cerrada")
    return redirect('/auth/login')