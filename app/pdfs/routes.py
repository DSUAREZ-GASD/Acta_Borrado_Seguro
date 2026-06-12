from flask import flash, send_file, redirect, url_for, abort, after_this_request
from flask_login import login_required
from . import pdf
from .generator import generar_pdf
import zipfile
import os
import io
import re
from flask_babel import _
from app.utils import acceso_requerido

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
@acceso_requerido(roles=["Administrador", "Agente_3"])
@login_required
def crear_pdf(tipo, obj_id):
    from app.models import Equipo, Actividad_verificacion, Representante, ActaConfig
    
    representantes = Representante.query.all()
    
    if tipo == 'equipo':
        objeto = Equipo.query.get_or_404(obj_id)  # Usa get_or_404 directo sobre PK
        tipo_config = 'borrado'
        nombre_base = objeto.nombre
    elif tipo == 'verificacion':
        objeto = Actividad_verificacion.query.get_or_404(obj_id)
        tipo_config = 'verificacion'
        nombre_base = objeto.equipo.nombre if objeto.equipo else f"Acta_{objeto.id}"
    else:
        abort(404)
    
    config_campos = ActaConfig.query.filter_by(
        tipo_acta=tipo_config, 
        es_visible=True
    ).order_by(ActaConfig.orden).all()
    
    nombre_archivo = f"Acta_{tipo_config}_{limpiar_nombre(nombre_base)}.pdf"
    
    # Generar el PDF
    ruta_pdf = generar_pdf(nombre_archivo, objeto, representantes, config_campos, tipo_config)
    
    @after_this_request
    def remover_temporal(response):
        borrar_archivo(ruta_pdf)
        return response

    return send_file(ruta_pdf, as_attachment=True, download_name=nombre_archivo)


@pdf.route('/generar_todos_pdfs/<string:tipo>', methods=['POST'])
@acceso_requerido(roles=["Administrador", "Agente_3"])
@login_required
def generar_todos_pdfs(tipo):
    """
    Descarga masiva unificada en ZIP. Soporta tipo 'equipo' (borrado) o 'verificacion'.
    """
    from app.models import Equipo, Actividad_verificacion, Representante, ActaConfig
    
    representantes = Representante.query.all()
    buffer = io.BytesIO()
    
    if tipo == 'equipo':
        # Equipos que tengan el campo imágenes con datos
        elementos = Equipo.query.filter(Equipo.imagenes != None).all()
        tipo_config = 'borrado'
    elif tipo == 'verificacion':
        # Actividades activas registradas en el sistema
        elementos = Actividad_verificacion.query.filter_by(activo=True).all()
        tipo_config = 'verificacion'
    else:
        abort(400, description="Tipo de lote inválido")

    if not elementos:
        flash("No se encontraron registros con evidencias para procesar este lote.", "info")
        return redirect(url_for('acta_verificacion.lista') if tipo == 'verificacion' else url_for('equipo.lista'))

    config_campos = ActaConfig.query.filter_by(tipo_acta=tipo_config, es_visible=True).order_by(ActaConfig.orden).all()

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for item in elementos:
            try:
                if tipo_config == 'borrado':
                    nombre_descarga = item.nombre
                else:
                    nombre_descarga = item.equipo.nombre if item.equipo else f"Acta_{item.id}"
                
                nombre_pdf = f"Acta_{tipo_config}_{limpiar_nombre(nombre_descarga)}.pdf"
                
                # Generación física individual
                ruta_temp = generar_pdf(nombre_pdf, item, representantes, config_campos, tipo_config)
                
                zip_file.write(ruta_temp, arcname=nombre_pdf)
                borrar_archivo(ruta_temp)
                
            except Exception as e:
                print(f"Error procesando lote en elemento ID {item.id}: {e}")

    buffer.seek(0)
    return send_file(
        buffer, 
        as_attachment=True, 
        download_name=f'paquete_actas_{tipo_config}.zip', 
        mimetype='application/zip'
    )