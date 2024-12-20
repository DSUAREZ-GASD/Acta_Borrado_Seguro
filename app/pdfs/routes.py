from flask import flash, send_file, current_app,redirect, url_for
from flask_login import current_user, login_required
from app import directory_exists
from app.auth.routes import acceso_requerido
from . import pdf
from .generator import  generar_pdf
import zipfile
import os
import threading
import time
from flask_babel import _ # type: ignore

def eliminar_archivo_temporal(ruta, delay):
    def eleminar():
        time.sleep(delay)
        try:
            if os.path.exists(ruta):
                os.remove(ruta)
                print(f"Archivo {ruta} eliminado")
        except Exception as e:
            print(f"Error eliminando archivo {ruta}: {e}")
    
    kill = threading.Thread(target=eleminar)
    kill.start()
    

@pdf.route('/crear_pdf/<int:equipo_id>', methods=['GET'])
@acceso_requerido(roles=["Administrador", "Agente"])
@login_required
def crear_pdf(equipo_id):
    try:
        # Importar equipo aquí en lugar de al inicio
        from app.models import Equipo, Representante
        equipo = Equipo.query.get_or_404(equipo_id)
        representantes = Representante.query.all()
        
        # Verificar que el estado del equipo sea finalizado 
        # if equipo.estado.value != "Finalizado":
        #     flash(_("El estado del equipo tiene que ser finalizado para que se generar el pdf"), "error")
        #     if current_user.rol.value == "Administrador":
        #         return redirect(url_for('equipos.lista_equipos'))
        #     elif current_user.rol.value == "Agente":
        #         return redirect(url_for('equipos.lista_equipos_agente'))
        
        nombre_archivo = f"{equipo.nombre}.pdf"
                
        # Generar el PDF
        ruta_pdf = generar_pdf(nombre_archivo, equipo, representantes)
        
        eliminar_archivo_temporal(ruta_pdf, 3600);   
        
        return send_file(ruta_pdf, as_attachment=True, mimetype='application/pdf')
        
    except Exception as e:
        flash(_("Error al crear el pdf {}").format(e), "error")
        return redirect(url_for('equipos.lista_equipos'))
         
@pdf.route('/generar_todos_pdfs', methods=['POST'])
@acceso_requerido(roles=["Administrador","Agente"])
@login_required
def generar_todos_pdfs():
    try:
        # Importar equipo y representante
        from app.models import Equipo, Representante
        equipos = Equipo.query.all()
        representante = Representante.query.all()
        
        if not representante:
             flash(_("No hay representante registrado en el sistema."), "error")
             return redirect(url_for('equipos.lista_equipos') if current_user.rol.value == "Administrador" else url_for('equipos.lista_equipos_agente'))

        #Generar PDF para cada equipo
        rutas_pdf = []
        equipos_sin_pdf = []
        for equipo in equipos:
            # # Verificar que el estado del equipo sea finalizado
            # if equipo.estado.value != "Finalizado":
            #     equipos_sin_pdf.append(equipo.nombre)
            #     continue # Omitir estos equipos
            
            #Llamamos a la función generar_pdf
            try:
                nombre_archivo = f"{equipo.nombre}.pdf"
                ruta_pdf = generar_pdf(nombre_archivo, equipo, representante)
                rutas_pdf.append(ruta_pdf)
            except Exception as e:
                flash(_(f"Error generando PDF para {equipo.nombre}.").format(e), "error")
    
        if rutas_pdf:
            zip_file = os.path.join(current_app.root_path,'static','tmp','actas_pdfs.zip')
            directory_exists(zip_file)
            with zipfile.ZipFile(zip_file, 'w') as zip_ref:
                for ruta_pdf in rutas_pdf:
                    zip_ref.write(ruta_pdf, os.path.basename(ruta_pdf)) # Añadir el archivo al zip
                    
            # Limpiar los archivos PDF temporales
            for ruta_pdf in rutas_pdf:
                os.remove(ruta_pdf)
            
            eliminar_archivo_temporal(zip_file, 3600)
                
            return send_file(zip_file, as_attachment=True, mimetype='application/zip', download_name='actas_pdfs.zip')
        
        if not rutas_pdf:
            flash(_("No se generaron PDFs para ningún equipo con estado 'finalizado'."), "info")
        
        # Si hay equipos que no cumplen la condición, mostrar un mensaje
        if equipos_sin_pdf:
            flash(_(f"No se generaron PDFs para los siguientes equipos: {', '.join(equipos_sin_pdf)}. El estado debe ser 'finalizado'."), "info")
        
        return redirect(url_for('equipos.lista_equipos') if current_user.rol.value == "Administrador" else url_for('equipos.lista_equipos_agente'))
    
    except Exception as e:
        flash(_("Ocurrió un error al generar los PDFs."), "error")
        return redirect(url_for('equipos.lista_equipos') if current_user.rol.value == "Administrador" else url_for('equipos.lista_equipos_agente'))
    
    