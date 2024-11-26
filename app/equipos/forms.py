from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField, SubmitField, FieldList #Tipos de datos d formulario
from flask_wtf.file import FileField,FileAllowed #Tipos de archivos que se van a cargar
from wtforms.validators import InputRequired, Optional, Length #Validaciones de formulario

class EquipoForm():
    nombre = StringField("Nombre del equipo:",
                         validators=[
                             InputRequired(message="Por favor ingresa un nombre de equipo"),
                             Length(max=50, message="El nombre del equipo no debe exceder los 50 caracteres")
                         ])
    comision = StringField("Comisión:",
                           validators=[
                               InputRequired(message="Por favor ingresa una comisión"),
                               Length(max=50, message="La comisión no debe exceder los 50 caracteres")
                           ])
    municipio = StringField("Municipio:",
                            validators=[
                                InputRequired(message="Por favor ingresa un municipio"),
                                Length(max=50, message="El municipio no debe exceder los 50 caracteres")
                            ])
    departamento = StringField("Departamento:",
                               validators=[
                                   InputRequired(message="Por favor ingresa un departamento"),
                                   Length(max=50, message="El departamento no debe exceder los 50 caracteres")
                               ])
    equipo_marca = StringField("Marca de equipo:",
                               validators=[
                                   InputRequired(message="Por favor ingresa una marca"),
                                   Length(max=50, message="La marca no debe exceder los 50 caracteres")
                               ])
    equipo_modelo = StringField("Modelo de equipo:",
                                validators=[
                                    InputRequired(message="Por favor ingresa un modelo"),
                                    Length(max=50, message="El modelo no debe exceder los 50 caracteres")
                                ])
    equipo_serial = StringField("Serial de equipo:",
                                validators=[
                                    InputRequired(message="Por favor ingresa un serial"),
                                    Length(max=50, message="El serial no debe exceder los 50 caracteres")
                                ])
    dd_marca = StringField("Marca de disco duro:",
                           validators=[
                               InputRequired(message="Por favor ingresa la marca del disco duro"),
                               Length(max=50, message="La marca del disco duro no debe exceder los 50 caracteres")
                           ])
    dd_modelo = StringField("Modelo de disco duro:",
                            validators=[
                                InputRequired(message="Por favor ingresa el modelo del disco duro"),
                                Length(max=50, message="El modelo del disco duro no debe exceder los 50 caracteres")
                            ])
    dd_serial = StringField("Serial de disco duro:",
                            validators=[
                                InputRequired(message="Por favor ingresa el serial del disco duro"),
                                Length(max=50, message="El serial del disco duro no debe exceder los 50 caracteres")
                            ])
    sha_1 = StringField("HASH (SHA-1):",
                        validators=[
                            InputRequired(message="Por favor ingresa el SHA-1"),
                            Length(max=50, message="El SHA-1 no debe exceder los 50 caracteres")
                        ])
    md_5 = StringField("HASH (MD-5):",
                       validators=[
                           InputRequired(message="Por favor ingresa el MD 5"),
                           Length(max=50, message="El MD 5 no debe exceder los 50 caracteres")
                       ])
    observacion = TextAreaField("Observaciones:",
                                validators=[Optional()])
    imagenes = FieldList(FileField("Imagen de equipo", validators=[
                            Optional(),
                            FileAllowed(['jpg', 'png'], message='Solo se admiten imágenes')
                         ]), min_entries=8, max_entries=8)
    
#Definir el formulario de registro de equipos
class NuevoEquipo(FlaskForm, EquipoForm):
    
    submit = SubmitField("Registrar equipo")
    
#Formulario de editar equipo    
class EditEquipoForm(FlaskForm, EquipoForm):
    
    submit=SubmitField("Actualizar equipo")
    




    
    
    