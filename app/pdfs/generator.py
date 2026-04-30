import os
from flask import current_app, render_template
from weasyprint import HTML
from app.models import ActaConfig

def generar_pdf(nombre_archivo, objeto, representantes, config_campos=None):
    """Genera un PDF usando WeasyPrint a partir de un template HTML."""
    
    # 1. Configuración de rutas
    ruta_pdf = os.path.join(current_app.root_path, 'static', 'tmp', nombre_archivo)
    os.makedirs(os.path.dirname(ruta_pdf), exist_ok=True)
    
    # 2. Lógica de campos dinámicos (Si no vienen de la ruta, se buscan aquí)
    if config_campos is None:
        # Si tiene comision es borrado, si no, es verificacion
        tipo_acta = 'borrado' if hasattr(objeto, 'comision') else 'verificacion'
        config_campos = ActaConfig.query.filter_by(
            tipo_acta=tipo_acta, 
            es_visible=True
        ).order_by(ActaConfig.orden).all()

    # 3. Selección de la plantilla correcta
    if hasattr(objeto, 'comision'):
        template_name = 'pdf/borrado_seguro.html'
    else:
        template_name = 'pdf/verificacion_tecnica.html'

    # 4. PREPARAR EL CONTEXTO (Debe ir ANTES de render_template)
    contexto = {
        'objeto': objeto,
        'representantes': representantes,
        'configuracion_acta': config_campos,
        'getattr': getattr,
        'hasattr': hasattr,
        'os': os,
        'base_path': current_app.root_path
    }

    # 5. Renderizado y Generación
    try:
        # Renderizamos el HTML con los datos
        html_content = render_template(template_name, **contexto)
        
        # Convertimos a PDF
        # base_url es fundamental para que WeasyPrint cargue imágenes de /static
        HTML(string=html_content, base_url=current_app.root_path).write_pdf(ruta_pdf)
        
    except Exception as e:
        print(f"Error crítico en la generación del PDF ({template_name}): {e}")
        raise e

    return ruta_pdf