from flask import flash, send_file, current_app,redirect, url_for
from flask_login import current_user, login_required
from app import directory_exists
from app.auth.routes import acceso_requerido
from . import pdf
from .generator import  generar_pdf
import zipfile
import os
import io
import re
from flask_babel import _


def borrar_archivo(ruta):
    try:
        if os.path.exists(ruta): os.remove(ruta)
    except: pass
    
def limpiar_nombre(nombre):
    nombre = nombre.strip()
    nombre = re.sub(r'[^\w\- ]', '', nombre)
    nombre = nombre.replace(' ', '_')
    return nombre

@pdf.route('/crear_pdf/<int:equipo_id>')
@login_required
def crear_pdf(equipo_id):
    from app.models import Equipo, Representante
    equipo = Equipo.query.get_or_404(equipo_id)
    representantes = Representante.query.all()
    
    nombre_archivo = f"{limpiar_nombre(equipo.nombre)}.pdf"
    
    # Generar físicamente
    ruta_pdf = generar_pdf(nombre_archivo, equipo, representantes)
    
    # Enviamos el archivo y programamos el borrado
    return send_file(ruta_pdf, as_attachment=True, download_name=nombre_archivo)
         
@pdf.route('/generar_todos_pdfs', methods=['POST'])
@login_required
def generar_todos_pdfs():
    from app.models import Equipo, Representante
    # Solo traer equipos que tengan imágenes para evitar PDFs vacíos
    equipos = Equipo.query.filter(Equipo.imagenes != None).all()
    representantes = Representante.query.all()

    if not equipos:
        flash("No hay equipos para procesar", "info")
        return redirect(url_for('equipos.lista_equipos'))

    # Creamos el ZIP en memoria primero para que sea más rápido
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for equipo in equipos:
            try:
                nombre = f"{limpiar_nombre(equipo.nombre)}.pdf"
                # Generamos el PDF temporalmente
                ruta_temp = generar_pdf(nombre, equipo, representantes)
                
                # Lo metemos al ZIP
                zip_file.write(ruta_temp, arcname=nombre)
                
                # Borramos el PDF individual inmediatamente para no llenar el disco
                borrar_archivo(ruta_temp)
            except Exception as e:
                print(f"Error en equipo {equipo.id}: {e}")

    buffer.seek(0)
    return send_file(
        buffer, 
        as_attachment=True, 
        download_name='actas_completas.zip', 
        mimetype='application/zip'
    )
    
    