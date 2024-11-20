from flask_wtf import FlaskForm
from wtforms import StringField,EmailField,PasswordField,SubmitField, SelectField
from wtforms.validators import InputRequired, Optional
from enum import Enum

# Columnas de atributos enumerados
class Rol(Enum):
    AGENTE = "Agente"
    ADMINISTRADOR = "Administrador"
    

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
                       validators= [Optional()])
     
     
class PerfilForm():
    
    userName=StringField("Nombre del Usuario:",
                         validators= [InputRequired(message="por favor ingresa un nombre de usuario")])
    email=EmailField("Correo del Usuario:",
                     validators= [InputRequired(message="por favor ingresa el correo del usuario")])
    
    rol = SelectField("Rol del Usuario:",
                      choices=[(rol.name, rol.value)for rol in Rol],
                      validators= [InputRequired(message="por favor ingresa el rol del usuario")])
    
    password=PasswordField("Contraseña de usuario:",
                           validators= [Optional()])
    
class NuevoUsuario(FlaskForm,UsuarioForm):
    
    submit = SubmitField("Registrar Usuario")
    
class EditUsuarioForm(FlaskForm,UsuarioForm):
    # current_password = PasswordField("Contraseña Actual:",
    #                                   validators=[InputRequired(message="Por favor ingresa tu contraseña actual.")])
    submit = SubmitField("Actualizar Datos")    
    
class PerfilUsuarioForm(FlaskForm,PerfilForm):  
    submit = SubmitField("Guardar Cambios")    
    
    
