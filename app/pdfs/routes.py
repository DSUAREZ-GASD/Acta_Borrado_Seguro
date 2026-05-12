from flask import flash, send_file, redirect, url_for, abort, after_this_request
from flask_login import login_required
from . import pdf
from .generator import generar_pdf
import zipfile
import os
import io
import re
from flask_babel import _

def borrar_archivo(ruta):
    try:
        if os.path.exists(ruta): 
            os.remove(ruta)
    except Exception as e: 
        print(f"Error al borrar temporal: {e}")

def limpiar_nombre(nombre):
    if not nombre: return "documento"
    nombre = nombre.strip()
    nombre = re.sub(r'[^\w\- ]', '', nombre)
    nombre = nombre.replace(' ', '_')
    return nombre

@pdf.route('/crear_pdf/<string:tipo>/<int:obj_id>')
@login_required
def crear_pdf(tipo, obj_id):
    from app.models import Equipo, Actividad_verificacion, Representante, ActaConfig
    
    # 1. Obtener representantes (Firmas)
    representantes = Representante.query.all()
    
    # 2. Determinar modelo y tipo de configuración
    if tipo == 'equipo':
        objeto = Equipo.query.filter_by(asd_id=obj_id).first_or_404()
        tipo_config = 'borrado'
    elif tipo == 'verificacion':
        objeto = Actividad_verificacion.query.filter_by(asd_id=obj_id).first_or_404()
        tipo_config = 'verificacion'
    else:
        abort(404)
    
    # 3. Obtener la configuración de campos que el Admin activó
    config_campos = ActaConfig.query.filter_by(
        tipo_acta=tipo_config, 
        es_visible=True
    ).order_by(ActaConfig.orden).all()
    
    nombre_archivo = f"{limpiar_nombre(objeto.nombre)}.pdf"
    
    # 4. Generar físicamente el PDF
    # Pasamos config_campos para que el template sepa qué columnas renderizar
    ruta_pdf = generar_pdf(nombre_archivo, objeto, representantes, config_campos, tipo_config)
    
    # 5. Programar el borrado del archivo después de enviarlo
    @after_this_request
    def remover_temporal(response):
        borrar_archivo(ruta_pdf)
        return response

    return send_file(ruta_pdf, as_attachment=True, download_name=nombre_archivo)

@pdf.route('/generar_todos_pdfs', methods=['POST'])
@login_required
def generar_todos_pdfs():
    from app.models import Equipo, Representante, ActaConfig
    
    # Solo equipos con evidencias
    equipos = Equipo.query.filter(Equipo.imagenes != None).all()
    representantes = Representante.query.all()
    config_campos = ActaConfig.query.filter_by(tipo_acta='borrado', es_visible=True).all()

    if not equipos:
        flash("No hay equipos con evidencias para procesar", "info")
        return redirect(url_for('equipos.lista_equipos'))

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for equipo in equipos:
            try:
                nombre = f"{limpiar_nombre(equipo.nombre)}.pdf"
                # Generamos el PDF temporal
                ruta_temp = generar_pdf(nombre, equipo, representantes, config_campos)
                
                # Agregar al ZIP
                zip_file.write(ruta_temp, arcname=nombre)
                
                # Limpieza inmediata del temporal individual
                borrar_archivo(ruta_temp)
            except Exception as e:
                print(f"Error procesando equipo {equipo.nombre}: {e}")

    buffer.seek(0)
    return send_file(
        buffer, 
        as_attachment=True, 
        download_name='paquete_actas_borrado.zip', 
        mimetype='application/zip'
    )