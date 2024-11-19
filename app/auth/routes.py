from . import auth
#el . es para que nos importe todo el modulo
from flask import render_template, redirect, flash
from .forms import LoginForm
import app
from flask_login import login_user, logout_user, current_user,login_required
from functools import wraps
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, JWTManager


jwt = JWTManager()


def acceso_requerido(roles=[]):
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


#ruta de login
@auth.route('/login', methods = ['GET','POST'])
def login():
    f = LoginForm()
    try:
        if f.validate_on_submit():
            u = app.models.Usuario.query.filter_by(userName=f.userName.data).first()
            
            if u is None:
                print("Usuario no existe")
                flash("No exite el usuario")
                return redirect('/auth/login')
            if u.check_password(f.password.data) is False:
                print("la contraseña es erronea")
                flash("clave errónea")
                return redirect('/auth/login')
            
            login_user(u,True)
            access_token = create_access_token(identity={'userName': u.userName, 'rol': u.rol.value})
            print(f"Token generado: {access_token}")
            
            if u.rol.value == "Administrador":
                print(f"Acesso al programa por {u.rol.value}")
                flash("Bienvenido a Equipos")
                return redirect('/equipos/listar')
            elif u.rol.value == "Agente":
                print(f"Acesso al programa por {u.rol.value}")
                flash("Bienvenido a Equipos")
                return redirect('/equipos/lista_agente')
            else:
                flash("Tu usuario no tiene rol asignado")
                return redirect('/auth/login')
            
           
    except Exception as e:
        flash(f"Ocurrió un error: {e}")
        return redirect('/auth/login')
 
    return render_template("login.html",f=f)


#ruta de logout
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("sesión cerrada")
    return redirect('/auth/login')


#Ruta protegida
@auth.route('/protegida')
@jwt_required()
def protegida():
    current_user = get_jwt_identity()
    return f"¡Hola, {current_user}!", 200
