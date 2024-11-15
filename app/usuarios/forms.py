from flask_wtf import FlaskForm
from wtforms import StringField,EmailField,PasswordField,SubmitField, SelectField
from wtforms.validators import InputRequired
from enum import Enum

# Columnas de atributos enumerados
class Rol(Enum):
    ADMINISTRADOR = "Administrador"
    AGENTE = "Agente"

#Formulario Maestro de cliente
class UsuarioForm():
     userName=StringField("Nombre del Usuario:",
                       validators= [InputRequired(message="por favor ingresa un nombre de usuario")])
     
     email=EmailField("Correo del Usuario:",
                       validators= [InputRequired(message="por favor ingresa el correo del usuario")])
     
     rol = SelectField("Rol del Usuario:",
                       choices=[(rol.name, rol.value)for rol in Rol],
                       validators= [InputRequired(message="por favor ingresa el rol del usuario")])
     
     password=PasswordField("Contraseña de usuario:",
                       validators= [InputRequired(message="por favor ingresa la contraseña del usuario")])
    

class NuevoUsuario(FlaskForm,UsuarioForm):
    submit = SubmitField("Registrar Usuario")
    
class EditUsuarioForm(FlaskForm,UsuarioForm):
    submit = SubmitField("Actualizar Datos")    
    
