from flask import render_template
from weasyprint import HTML
from app.models import ActaConfig
import os

class PDFService:
    @staticmethod
    def generar_acta(tipo, objeto):
        # 1. Obtener la configuración de campos del Admin
        config = ActaConfig.query.filter_by(tipo_acta=tipo).order_by(ActaConfig.orden).all()
        
        # 2. Renderizar HTML con Jinja2
        # El getattr es clave para que _metadata.html funcione
        html_string = render_template(
            f'pdf/{tipo if tipo == "verificacion" else "borrado_seguro"}.html',
            objeto=objeto,
            configuracion_acta=config,
            getattr=getattr
        )
        
        # 3. Convertir a PDF con WeasyPrint
        # Opcional: pasar base_url para que encuentre las imágenes en /static
        pdf = HTML(string=html_string).write_pdf()
        
        return pdf