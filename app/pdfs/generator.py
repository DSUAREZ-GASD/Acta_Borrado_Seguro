import os
from flask import current_app, render_template
from weasyprint import HTML
from app.models import ActaConfig

def generar_pdf(nombre_archivo, objeto, representantes, config_campos=None, tipo_acta=None):
    """Genera un PDF usando WeasyPrint a partir de un template HTML."""
    
    # Configuración de rutas
    ruta_pdf = os.path.join(current_app.root_path, 'static', 'tmp', nombre_archivo)
    os.makedirs(os.path.dirname(ruta_pdf), exist_ok=True)
    
    # 1. Determinar el tipo de acta si no viene de la ruta
    
    if tipo_acta is None:
        # Fallback de seguridad (aunque lo ideal es que venga de la ruta)
        # Si es Actividad_verificacion, suele tener 'asd_id' pero podemos ser más específicos:
        tipo_acta = 'verificacion' if 'Actividad_verificacion' in str(type(objeto)) else 'borrado'
    
    # 2. Lógica de campos dinámicos
    if config_campos is None:
        config_campos = ActaConfig.query.filter_by(
            tipo_acta=tipo_acta, 
            es_visible=True
        ).order_by(ActaConfig.orden).all()

    # 3. SELECCIÓN DE LA PLANTILLA BASADA EN TIPO_ACTA (No en atributos)
    if tipo_acta == 'verificacion':
        template_name = 'pdf/verificacion_tecnica.html'
    else:
        template_name = 'pdf/borrado_seguro.html'

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
    # 5. Renderizado y Generación
    try:
        html_content = render_template(template_name, **contexto)
        HTML(string=html_content, base_url=current_app.root_path).write_pdf(ruta_pdf)
    except Exception as e:
        print(f"Error crítico en la generación del PDF ({template_name}): {e}")
        raise e

    return ruta_pdf