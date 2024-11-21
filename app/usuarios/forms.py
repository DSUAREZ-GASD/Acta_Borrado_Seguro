from flask_wtf import FlaskForm
from wtforms import StringField,EmailField,PasswordField,SubmitField, SelectField
from wtforms.validators import InputRequired, Optional
from enum import Enum

# Columnas de atributos enumerados
class Rol(Enum):
    AGENTE = "Agente"
    ADMINISTRADOR = "Administrador"
    
class Estado_usuario(Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"    

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
    
    current_password = PasswordField("Contraseña Actual:",
                                     validators=[InputRequired(message="Por favor ingresa tu contraseña actual.")])
    
    password=PasswordField("Contraseña de usuario:",
                           validators= [Optional()])
    
    confirm_password=PasswordField("Confirma la contraseña:",
                                  validators= [Optional()])
    
    
class cambio_password():
    current_password = PasswordField("Contraseña Actual:",
                                        validators=[InputRequired(message="Por favor ingresa tu contraseña actual.")])
    
    password=PasswordField("Nueva contraseña:",
                            validators= [InputRequired(message="Por favor ingresa tu contraseña actual.")])
    
    confirm_password=PasswordField("Confirma la contraseña:",
                                   validators= [InputRequired(message="Por favor ingresa tu contraseña actual.")])
    
class NuevoUsuario(FlaskForm,UsuarioForm):
    
    submit = SubmitField("Registrar Usuario")
    
class EditUsuarioForm(FlaskForm,UsuarioForm):
    
    estado = SelectField("Estado del Usuario:",
                         choices=[(estado.name, estado.value) for estado in Estado_usuario],
                         validators=[InputRequired(message="Por favor ingresa el estado del usuario")])

    submit = SubmitField("Actualizar Datos")    
    
class PerfilUsuarioForm(FlaskForm,PerfilForm):  
    submit = SubmitField("Guardar Cambios")    


class CambiarPasswordForm(FlaskForm,cambio_password):
    submit = SubmitField("Cambiar Contraseña")
    
    
