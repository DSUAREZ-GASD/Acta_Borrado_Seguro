from flask import render_template, redirect, flash, request, url_for
from flask_login import login_required, current_user
from flask_babel import _ # type: ignore
from . import acta_verificacion
from app import db
from app.auth.routes import acceso_requerido
from app.models import Actividad_verificacion, EstadoEnum
from .forms import Nueva_Acta_Verificacion, Edit_Acta_Verificacion
from app.utils import guardar_imagen_estandarizada, limpiar_imagenes_huerfanas
from app.utils.evaluador_flujo import evaluar_estado_verificacion


labels = {
    0: "1.	Proceso de Montado imagen de Copia de seguridad",
    1: "2. Contenido Unidad C:/",
    2: "3. Carpeta C:/ELE_ESCRUTINIOS_LOCALES_EVENTO",
    3: "4. Carpeta C:/SoftwareBaseCongresoConsulta",
    4: "5. Carpeta C:/LICENCIAS_ASD",
    5: "6. Carpeta para segunda vuelta 1",
    6: "7. Carpeta para segunda vuelta 2"
}

@acta_verificacion.route('/crear', methods=["GET", "POST"])
@acceso_requerido(roles=["Administrador"])
@login_required
def crear():
    form = Nueva_Acta_Verificacion()
    if form.validate_on_submit():
        try:
            actividad = Actividad_verificacion()
            
            es_log_valido = form.confirmar_log.data
            del form['confirmar_log']
            
            form.populate_obj(actividad)
            
            # Forzamos la escritura de la nota si se marcó el checkbox
            if es_log_valido:
                nota_log = "[LOG VERIFICADO Y VALIDADO CON ÉXITO]"
                actividad.observacion = f"{form.observacion.data or ''} - {nota_log}".strip(" - ")
            
            actividad.examinador_id = form.examinador_select.data.id if form.examinador_select.data else None
            actividad.usuario_id = current_user.id
            
            # --- BLINDAJE POSICIONAL DE 7 IMÁGENES ---
            lista_imagenes = []
            for i in range(7):
                campo_imagen = form.evidencias[i] if i < len(form.evidencias.entries) else None
                if campo_imagen and campo_imagen.data and hasattr(campo_imagen.data, 'filename') and campo_imagen.data.filename != '':
                    nombre_foto = guardar_imagen_estandarizada(campo_imagen.data, subfolder='verificaciones')
                    lista_imagenes.append(nombre_foto)
                else:
                    lista_imagenes.append(None)
            actividad.evidencias = lista_imagenes
            
            # --- SOLUCIÓN: DELEGACIÓN ÚNICA AL MODELO ---
            # El modelo ejecutará el evaluador internamente conservando los cambios de observacion
            actividad.actualizar_estado()

            db.session.add(actividad)
            db.session.commit()
            
            # Mensajes Flash dinámicos basados en la resolución del modelo
            if actividad.estado in [EstadoEnum.PENDIENTE_HASH, EstadoEnum.PENDIENTE_LOG]:
                flash("Acta guardada pero incompleta: Requiere HASH y validación de LOG.", "warning")
            elif actividad.estado == EstadoEnum.FINALIZADO:
                flash("Verificación completada con éxito.", "success")
            else:
                flash("Acta registrada correctamente.", "info")
                
            return redirect(url_for('acta_verificacion.lista'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar actividad: {e}", "error")
            
    return render_template('acta_verificacion/crear.html', form=form, labels=labels)


# Ruta para listar los equipos por administrador
@acta_verificacion.route('/lista')
@acceso_requerido(roles=["Administrador", "Agente_3"])
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
        
        nota_log = "[LOG VERIFICADO Y VALIDADO CON ÉXITO]"
        if actividad.observacion and nota_log in actividad.observacion:
            form.confirmar_log.data = True  # Esto marcará automáticamente el checkbox en el HTML
        else:
            form.confirmar_log.data = False

    while len(form.evidencias.entries) < 7:
        form.evidencias.append_entry()

    if form.validate_on_submit():
        try:
            fotos_previas = actividad.evidencias if actividad.evidencias else [None] * 7
            
            es_log_valido = form.confirmar_log.data
            del form['confirmar_log']
            
            form.populate_obj(actividad)
            
            # Forzamos y blindamos el String en la edición
            if es_log_valido:
                nota_log = "[LOG VERIFICADO Y VALIDADO CON ÉXITO]"
                if not actividad.observacion or nota_log not in actividad.observacion:
                    actividad.observacion = f"{actividad.observacion or ''} {nota_log}".strip()
            
            actividad.examinador_id = form.examinador_select.data.id if form.examinador_select.data else None
            actividad.usuario_id = current_user.id
            
            # --- RECONSTRUCCIÓN POSICIONAL PARA 7 IMÁGENES ---
            nuevas_evidencias = []
            for i in range(7):
                campo_imagen = form.evidencias[i]
                foto_antigua = fotos_previas[i] if i < len(fotos_previas) else None
                tiene_archivo_nuevo = campo_imagen.data and hasattr(campo_imagen.data, 'filename') and campo_imagen.data.filename != ''
                
                if tiene_archivo_nuevo:
                    nombre_nuevo = guardar_imagen_estandarizada(campo_imagen.data, subfolder='verificaciones')
                    nuevas_evidencias.append(nombre_nuevo)
                else:
                    nuevas_evidencias.append(foto_antigua)

            actividad.evidencias = nuevas_evidencias
            
            # --- SOLUCIÓN: DELEGACIÓN ÚNICA AL MODELO ---
            actividad.actualizar_estado()
            
            db.session.commit()
            
            try: limpiar_imagenes_huerfanas() 
            except: pass

            if actividad.estado in [EstadoEnum.PENDIENTE_HASH, EstadoEnum.PENDIENTE_LOG]:
                flash("Acta actualizada. Sigue pendiente el cumplimiento de HASH o LOG.", "warning")
            elif actividad.estado == EstadoEnum.FINALIZADO:
                flash("Acta de verificación finalizada con éxito.", "success")
            else:
                flash("Cambios aplicados correctamente.", "info")

            return redirect(url_for('acta_verificacion.lista'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {e}", "error")
            return redirect(url_for('acta_verificacion.editar', actividad_id=actividad_id))
        
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