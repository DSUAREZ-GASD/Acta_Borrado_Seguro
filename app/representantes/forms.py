from enum import Enum
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField#Tipos de datos d formulario
from flask_wtf.file import FileField, FileRequired,FileAllowed #Tipos de archivos que se van a cargar
from wtforms.validators import InputRequired, Optional, Length, Regexp #Validaciones de formulario

class Roles(Enum):
    REGISTRADURIA = "Registraduria"
    AUDITORIA = "Auditoria"
    PROCURADURIA = "Procuraduria"
    CONTRATISTA = "Contratista"


class representanteForm():
    nombre =  StringField("Ingreso de responsable:",
                        validators=[InputRequired(message="por favor ingresa un nombre de represetante"),
                                    Length(max=50, message="El nombre del equipo no debe exceder los 50 caracteres")])
    rol = SelectField("Rol del Usuario:",
                       choices=[(rol.name, rol.value)for rol in Roles],
                       validators= [InputRequired(message="por favor ingresa el rol del represetante")])
    firma =  FileField("Imagen de producto", validators=[
                            FileRequired(message="Debes ingresar un archivo"),
                            FileAllowed(['jpg', 'png','pdf','webp', 'jpeg'], message='Solo se admiten imágenes')])


class Nuevo_Representante(FlaskForm, representanteForm):
    submit = SubmitField('Registrar')
    
    
class EditRespresentanteForm(FlaskForm, representanteForm):
    firma =  FileField("Imagen de producto", validators=[
                            Optional(),
                            FileAllowed(['jpg', 'png','pdf'], message='Solo se admiten imágenes')])
    
    submit=SubmitField("Actualizar")