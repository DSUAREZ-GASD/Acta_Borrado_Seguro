from flask_wtf import FlaskForm
from wtforms import SubmitField, FieldList
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import Optional

class GestionarEvidenciasForm(FlaskForm):
    """
    Formulario exclusivo para la carga y custodia de evidencias fotográficas.
    Sustituye completamente a los formularios anteriores.
    """
    evidencias = FieldList(
        FileField(
            "Evidencia Fotográfica", 
            validators=[
                Optional(),
                FileAllowed(['jpg', 'png', 'webp', 'jpeg'], message='Solo se admiten imágenes')
            ]
        ), 
        min_entries=7, 
        max_entries=7
    )
    submit = SubmitField("Guardar Evidencias Fotográficas")