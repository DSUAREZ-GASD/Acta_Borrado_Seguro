from flask import render_template, redirect, flash, request, url_for
from flask_login import login_required, current_user
from flask_babel import _ # type: ignore
from . import acta_verificacion
from app import db
from app.auth.routes import acceso_requerido
from app.models import Actividad_verificacion
from .forms import Nueva_Acta_Verificacion, Edit_Acta_Verificacion
from app.utils import guardar_imagen_estandarizada, limpiar_imagenes_huerfanas


labels = {
    0: "1.	Proceso de Montado imagen de Copia de seguridad",
    1: "2. Contenido Unidad C:/",
    2: "3. Carpeta C:/ELE_ESCRUTINIOS_LOCALES_EVENTO",
    3: "4. Carpeta C:/SoftwareBaseCongresoConsulta",
    4: "5. Carpeta C:/LICENCIAS_ASD",
}

@acta_verificacion.route('/crear', methods=["GET", "POST"])
@acceso_requerido(roles=["Administrador"])
@login_required
def crear():
    form = Nueva_Acta_Verificacion()
    if form.validate_on_submit():
        try:
            actividad = Actividad_verificacion()
            
            form.populate_obj(actividad)
            
            if form.examinador_select.data:
                actividad.examinador_id = form.examinador_select.data.id
            else:
                actividad.examinador_id = None
                
            actividad.usuario_id = current_user.id
            
            # Procesar imágenes: Filtra solo las que tienen datos
            lista_evidencias = [
                guardar_imagen_estandarizada(f.data) 
                for f in form.evidencias if f.data
            ]
            
            actividad.evidencias = [img for img in lista_evidencias if img is not None]
            
            actividad.actualizar_estado()

            db.session.add(actividad)
            db.session.commit()
            
            flash(_("Registro de actividad exitoso"), "success")
            return redirect(url_for('acta_verificacion.lista_actividades'))
            
        except Exception as e:
            db.session.rollback()
            flash(_(f"Error al registrar actividad: {e}"), "error")
    else:
        print(form.errors)
            
    return render_template('acta_verificacion/crear.html', form=form, labels=labels)


# Ruta para listar los equipos por administrador
@acta_verificacion.route('/lista')
@acceso_requerido(roles=["Administrador"])
@login_required
def lista():
    try:
        actividades = Actividad_verificacion.query.all()
        return render_template('acta_verificacion/lista.html', actividades=actividades)
    except Exception as e:
        flash(_("Error al listar actividades: {}").format(e), "error")
        return redirect(url_for('equipo.lista'))
    
    
@acta_verificacion.route('/editar/<actividad_id>', methods=['GET', 'POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def editar(actividad_id):
    actividad = Actividad_verificacion.query.get_or_404(actividad_id)
    form = Edit_Acta_Verificacion(obj=actividad)
    
    if request.method == 'GET':
        form.examinador_select.data = actividad.examinador_rel

    # Rellenar entradas vacías para el formulario
    while len(form.evidencias.entries) < form.evidencias.max_entries:
        form.evidencias.append_entry()

    if form.validate_on_submit():
        
        try:
            # Respaldamos las fotos actuales antes de poblar el objeto
            fotos_previas = actividad.evidencias or []
            form.populate_obj(actividad)
            
            if form.examinador_select.data:
                actividad.examinador_id = form.examinador_select.data.id
            else:
                actividad.examinador_id = None
                
            
            
            nuevas_evidencias = []
            for i, campo_evidencia in enumerate(form.evidencias):
                # Si se subió un archivo nuevo, lo guardamos
                nombre_nuevo = guardar_imagen_estandarizada(campo_evidencia.data)
                
                if nombre_nuevo:
                    nuevas_evidencias.append(nombre_nuevo)
                elif i < len(fotos_previas):
                    # Si no hay archivo nuevo, mantenemos la que estaba en esa posición
                    nuevas_evidencias.append(fotos_previas[i])

            actividad.evidencias = nuevas_evidencias
            actividad.usuario_id = current_user.id
            actividad.actualizar_estado()
            
            db.session.commit()
            
            # Limpieza silenciosa
            try: limpiar_imagenes_huerfanas() 
            except: pass

            flash("Actividad actualizada exitosamente", "success")
            return redirect(url_for('acta_verificacion.lista'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {e}", "error")
            return redirect(url_for('acta_verificacion.editar', actividad_id=actividad_id))
    else:
        print(form.errors)
        
    return render_template('acta_verificacion/editar.html', form=form, actividad=actividad, labels=labels)

@acta_verificacion.route('/eliminar/<actividad_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def eliminar(actividad_id):
   actividad = Actividad_verificacion.query.get_or_404(actividad_id)
   try:
       if actividad:              
           db.session.delete(actividad)
           db.session.commit()
           flash(_("Actividad Eliminada con exito"), "success")
           limpiar_imagenes_huerfanas()
       else:
           flash(_("Actividad no encontrada"), "error")
   except Exception as e:
        db.session.rollback()
        flash(_("Error al eliminar la actividad: {}").format(e), "error")
   
   return redirect(url_for('acta_verificacion.lista'))