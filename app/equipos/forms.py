from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField, SubmitField, FieldList #Tipos de datos d formulario
from flask_wtf.file import FileField,FileAllowed #Tipos de archivos que se van a cargar
from wtforms.validators import InputRequired, Optional #Validaciones de formulario

class EquipoForm():
    nombre = StringField("Nombre del equipo:",
                       validators= [InputRequired(message="por favor ingresa un nombre de equipo")])
    comision = StringField("Comisión:",
                        validators=[InputRequired(message="por favor ingresa una comision")])
    municipio = StringField("Municipio:",
                            validators=[InputRequired(message="por favor ingresa un municipio")])
    departamento = StringField("Departamento:",
                               validators=[InputRequired(message="por favor ingresa un departamento")])
    equipo_marca = StringField("Marca de equipo:",
                               validators=[InputRequired(message="por favor ingresa una marca")])
    equipo_modelo = StringField("Modelo de equipo:",
                                validators=[InputRequired(message="por favor ingresa un modelo")])
    equipo_serial = StringField("Serial de equipo:",
                                validators=[InputRequired(message="por favor ingresa un serial")])
    dd_marca = StringField("Marca de disco duro:",
                           validators=[InputRequired(message="por favor ingresa la marca del disco duro")])
    dd_modelo = StringField("Modelo de disco duro:",
                            validators=[InputRequired(message="por favor ingresa el modelo del disco duro")])
    dd_serial = StringField("Serial de disco duro:",
                            validators=[InputRequired(message="por favor ingresa el serial del disco duro")])
    sha_1 = StringField("HASH (SHA-1):",
                        validators=[InputRequired(message="por favor ingresa el SHA-1")])
    md_5 = StringField("HASH (MD-5):",
                       validators=[InputRequired(message="por favor ingresa el MD 5")])
    observacion = TextAreaField("Observaciones:",
                                validators=[Optional()])
    
#Definir el formulario de registro de equipos
class NuevoEquipo(FlaskForm, EquipoForm):
    imagenes = FieldList(FileField("Imagen de equipo", validators=[
                            Optional(),
                            FileAllowed(['jpg', 'png'], message='Solo se admiten imágenes')
                         ]), min_entries=8, max_entries=8)
    
    submit = SubmitField("Registrar equipo")
    
#Formulario de editar equipo    
class EditEquipoForm(FlaskForm, EquipoForm):
    imagenes = FieldList(FileField("Imagen de equipo", validators=[
                            Optional(),
                            FileAllowed(['jpg', 'png'], message='Solo se admiten imágenes')
                         ]), min_entries=8, max_entries=8)
    
    submit=SubmitField("Actualizar")
    




    
    
    