from flask import flash, send_file, current_app,redirect
from . import pdf
from .generator import  generar_pdf
import zipfile
import os

@pdf.route('/generar_pdf/<int:equipo_id>')
def crear_pdf(equipo_id):
    try:
        # Importar equipo aquí en lugar de al inicio
        from app.models import Equipo, Registro_firma
        equipo = Equipo.query.get_or_404(equipo_id)
       
        # Verificar que el estado del equipo sea finalizado 
        if equipo.estado.value != "Finalizado":
            flash("El estado del equipo tiene que ser finalizado para que se generar el pdf")
            return redirect('/equipos/listar')
        
        firma = Registro_firma.query.first()
        nombre_archivo = f"{equipo.nombre}_prueba.pdf"  
                
        # Generar el PDF
        ruta_pdf = generar_pdf(nombre_archivo, firma, equipo)
        
        return send_file(ruta_pdf, as_attachment=True, mimetype='application/pdf')
        
    except Exception as e:
        print(f"Error generando PDF: {e}") 
        flash("No se pudo generar el PDF. Inténtalo de nuevo más tarde.")
        return redirect('/equipos/listar')
         

@pdf.route('/generar_todos_pdfs', methods=['POST'])
def generar_todos_pdfs():
    try:
        # Importar equipo y firma
        from app.models import Equipo, Registro_firma
        equipos = Equipo.query.all()
        firma = Registro_firma.query.first()
        
        if not firma:
            flash("No hay firma registrada")
            return redirect('/equipos/listar')

        #Generar PDF para cada equipo
        rutas_pdf = []
        equipos_sin_pdf = []
        for equipo in equipos:
            # Verificar que el estado del equipo sea finalizado
            if equipo.estado.value != "Finalizado":
                equipos_sin_pdf.append(equipo.nombre)
                continue # Omitir estos equipos
            
            #Llamamos a la función generar_pdf
            try:
                nombre_archivo = f"{equipo.nombre}_prueba.pdf"
                ruta_pdf = generar_pdf(nombre_archivo, firma, equipo)
                rutas_pdf.append(ruta_pdf)
            except Exception as e:
                print(f"Error generando PDF para {equipo.nombre}: {e}")
                flash(f"Error generando PDF para {equipo.nombre}.")
    
        if rutas_pdf:
            zip_file = os.path.join(current_app.root_path,'static','tmp','actas_pdfs.zip')
            with zipfile.ZipFile(zip_file, 'w') as zip_ref:
                for ruta_pdf in rutas_pdf:
                    zip_ref.write(ruta_pdf, os.path.basename(ruta_pdf)) # Añadir el archivo al zip
                    
            # Limpiar los archivos PDF temporales
            for ruta_pdf in rutas_pdf:
                os.remove(ruta_pdf)
                
            return send_file(zip_file, as_attachment=True, mimetype='application/zip', download_name='actas_pdfs.zip')
        
        if not rutas_pdf:
            flash("No se generaron PDFs para ningún equipo con estado 'finalizado'.")
        
        # Si hay equipos que no cumplen la condición, mostrar un mensaje
        if equipos_sin_pdf:
            flash(f"No se generaron PDFs para los siguientes equipos: {', '.join(equipos_sin_pdf)}. El estado debe ser 'finalizado'.")
        
        return redirect('/equipos/listar')
    
    except Exception as e:
        print(f"Error generando PDF: {e}")
        flash("Ocurrió un error al generar los PDFs.")
        return redirect('/equipos/listar')
    
    