from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import InputRequired, Length, Regexp
from flask_babel import gettext as _

#Formulario de login
class LoginForm(FlaskForm):
     userName=StringField(label="Ingresa un nombre",
                       validators= [InputRequired(message="por favor ingresa un nombre  de usuario")])
     
     
     password = PasswordField(_("Nueva Contraseña:"),
          validators=[InputRequired(message=_("Por favor ingresa tu nueva contraseña.")),
               Length(min=8, message=_("La contraseña debe tener al menos 8 caracteres")),
               Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[*#@.$£]).+$', 
               message=_("La contraseña debe contener al menos una letra mayúscula, una letra minúscula, un número y un carácter especial (*,#,@,.,$,£)"))
          ]
     )
    
     submit = SubmitField("Ingresar")
    
