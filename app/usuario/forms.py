from flask_wtf import FlaskForm
from wtforms import StringField,EmailField,PasswordField,SubmitField, SelectField
from wtforms.validators import InputRequired, Optional, Email, EqualTo, Length, Regexp
from flask_babel import gettext as _ # type: ignore
from enum import Enum

# Columnas de atributos enumerados
class Rol(Enum):
    AGENTE_OPERADOR = "Agente_1" 
    AGENTE_SUPERVISOR = "Agente_2"
    AGENTE_AUDITOR = "Agente_3"
    ADMINISTRADOR = "Administrador"
    
class EstadoUsuario(Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"    

# Formulario Maestro de usuario
class FormRegistrarUsuario(FlaskForm):
    
     nombre = StringField(_("Nombre:"),
                            validators=[InputRequired(message=_("Por favor ingresa el nombre del usuario")),
                                        Length(min=2, max=150, message=_("El nombre debe tener entre 2 y 150 caracteres"))])
     apellido = StringField(_("Apellido:"),
                            validators=[InputRequired(message=_("Por favor ingresa el apellido del usuario")),
                                        Length(min=2, max=150, message=_("El apellido debe tener entre 2 y 150 caracteres"))])
     userName=StringField(_("Nombre del Usuario:"),
                       validators= [InputRequired(message=_("Por favor ingresa un nombre de usuario")),
            Length(min=5, max=20, message=_("El nombre de usuario debe tener entre 5 y 20 caracteres"))])
     
     email = EmailField(_("Correo del Usuario:"),
                        validators=[InputRequired(message=_("Por favor ingresa el correo del usuario")),
                                    Email(message=_("Por favor ingresa un correo válido")),
                                    Regexp(r'^[\w\.-]+@grupoasd\.com$', message=_("El correo debe ser de la compañía '@grupoasd.com'"))])
    
     rol = SelectField('Rol', choices=[(r.value, r.value) for r in Rol])
    
     password = PasswordField(_("Contraseña de usuario:"),
        validators=[Optional()])
     
     submit = SubmitField("Registrar Usuario")
     
# Formulario de restablecimiento de usuario
class FormRestablecerUsuario(FlaskForm):
    
    nombre = StringField(_("Nombre:"),
                            validators=[InputRequired(message=_("Por favor ingresa el nombre del usuario")),
                                        Length(min=2, max=150, message=_("El nombre debe tener entre 2 y 150 caracteres"))])
    apellido = StringField(_("Apellido:"),
                            validators=[InputRequired(message=_("Por favor ingresa el apellido del usuario")),
                                        Length(min=2, max=150, message=_("El apellido debe tener entre 2 y 150 caracteres"))])
        
    userName=StringField(_("Nombre del Usuario:"),
                       validators= [InputRequired(message=_("Por favor ingresa un nombre de usuario")),
            Length(min=5, max=20, message=_("El nombre de usuario debe tener entre 5 y 20 caracteres"))])
     
    email = EmailField(_("Correo del Usuario:"),
                        validators=[InputRequired(message=_("Por favor ingresa el correo del usuario")),
                                    Email(message=_("Por favor ingresa un correo válido")),
                                    Regexp(r'^[\w\.-]+@grupoasd\.com$', message=_("El correo debe ser de la compañía '@grupoasd.com'"))])
    
    rol = SelectField('Rol', choices=[(r.value, r.value) for r in Rol])
     
    estado = SelectField("Estado del Usuario:",
                         choices=[(estado.name, estado.value) for estado in EstadoUsuario],
                         validators=[InputRequired(message="Por favor ingresa el estado del usuario")])
    
    password = PasswordField(_("Contraseña de usuario:"),
        validators=[Optional()])
     
    submit = SubmitField("Restablecer Usuario")
     
# Formulario de perfil de usuario     
class FormPerfil(FlaskForm):
    
    nombre = StringField(_("Nombre:"),
                            validators=[InputRequired(message=_("Por favor ingresa el nombre del usuario")),
                                        Length(min=2, max=150, message=_("El nombre debe tener entre 2 y 150 caracteres"))])
    apellido = StringField(_("Apellido:"),
                            validators=[InputRequired(message=_("Por favor ingresa el apellido del usuario")),
                                        Length(min=2, max=150, message=_("El apellido debe tener entre 2 y 150 caracteres"))])
    
    userName=StringField(_("Nombre del Usuario:"),
                       validators= [InputRequired(message=_("Por favor ingresa un nombre de usuario")),
            Length(min=5, max=20, message=_("El nombre de usuario debe tener entre 5 y 20 caracteres"))])
     
    email = EmailField(_("Correo del Usuario:"),
                        validators=[InputRequired(message=_("Por favor ingresa el correo del usuario")),
                                    Email(message=_("Por favor ingresa un correo válido")),
                                    Regexp(r'^[\w\.-]+@grupoasd\.com$', message=_("El correo debe ser de la compañía '@grupoasd.com'"))])
    
    current_password = PasswordField(_("Contraseña Actual:"),
                                     validators=[Optional(),Length(min=8, message=_("La contraseña debe tener al menos 8 caracteres")),
            Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[*#@.$£]).+$',message=_("Por favor ingresa tu contraseña actual."))])
    
    password=PasswordField(_("Nueva Contraseña:"),validators=[Optional(), Length(min=8, message=_("La contraseña debe tener al menos 8 caracteres")),
            Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[*#@.$£]).+$', message=_("La contraseña debe contener al menos una letra mayúscula, una letra minúscula, un número y un carácter especial (*,#,@,.,$,£)"))])
    
    confirm_password=PasswordField(_("Confirma la Contraseña:"),
                                   validators=[Optional(), EqualTo('password', message=_("Las contraseñas no coinciden"))])
    
    submit = SubmitField("Guardar Cambios")
    
# Formulario de cambio de contraseña
class FormNuevaClave(FlaskForm):
    current_password = PasswordField("Contraseña Actual:",
                                        validators=[InputRequired(message="Por favor ingresa tu contraseña actual.")])
    
    password = PasswordField(_("Nueva Contraseña:"),
        validators=[InputRequired(message=_("Por favor ingresa tu nueva contraseña.")),
            Length(min=8, message=_("La contraseña debe tener al menos 8 caracteres")),
            Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[*#@.$£]).+$', 
            message=_("La contraseña debe contener al menos una letra mayúscula, una letra minúscula, un número y un carácter especial (*,#,@,.,$,£)"))
        ]
    )
    
    confirm_password=PasswordField("Confirma la contraseña:",
                                   validators= [InputRequired(message="Por favor ingresa tu contraseña actual.")])
    
    submit = SubmitField("Cambiar Contraseña")     
