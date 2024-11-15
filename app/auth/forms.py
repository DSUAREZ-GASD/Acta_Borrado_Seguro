from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import InputRequired

#Formulario de login
class LoginForm(FlaskForm):
     userName=StringField(label="Ingresa un nombre",
                       validators= [InputRequired(message="por favor ingresa un nombre  de usuario")])
     
     
     password=PasswordField(label="Ingresa una clave",
                       validators= [InputRequired(message="por favor ingresa la contraseña")])
    
     submit = SubmitField("Ingresar")
    
