from flask import render_template, redirect, flash, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from flask_babel import _ # type: ignore
import os
import uuid
from . import equipos
from app import db, directory_exists
from app.auth.routes import acceso_requerido
from app.models import Equipo
from .forms import NuevoEquipo, EditEquipoForm

# Diccionario de labels para imagenes de equipo de los formularios
labels = {
    0: "Foto de la caja del equipo",
    1: "Foto del equipo",
    2: "Foto serial del equipo",
    3: "Foto de la Identificación de la comisión",
    4: "Foto inicio de generación de la imagen",
    5: "Foto finalización de la generación de la imagen",
    6: "Foto inicio del borrado",
    7: "Foto finalización del borrado",
}


# Ruta para crear un equipo
@equipos.route('/crear-equipo', methods=["GET","POST"])
@acceso_requerido(roles=["Administrador","Agente"])
@login_required
def crear_equipo():
    equipo = Equipo()
    form_registrar = NuevoEquipo()
    
    if form_registrar.validate_on_submit():
        try:
            # Poblar el objeto equipo
            form_registrar.populate_obj(equipo)
            equipo.imagenes = []
            equipo.usuario_id = current_user.id
           
            # Guardar cada imagen
            for imagen_field in form_registrar.imagenes:
                if imagen_field.data:
                    filename = imagen_field.data.filename
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join('app/static/img', unique_filename)
                    directory_exists(file_path)
                    imagen_field.data.save(file_path)
                    equipo.imagenes.append(unique_filename)
            
            # Agregar el equipo a la base de datos
            db.session.add(equipo)      
            db.session.commit()                
            flash(_("Registro de equipo exitoso"), "success")
            if current_user.rol.value == "Administrador":
                return redirect(url_for('equipos.lista_equipos'))
            elif current_user.rol.value == "Agente":
                return redirect(url_for('equipos.lista_equipos_agente'))
        except Exception as e:
            db.session.rollback()
            flash(_("Error al registrar equipo {}").format(e), "error")
            
    return render_template('crear_equipo.html', form=form_registrar, labels=labels)

# Ruta para listar los equipos por administrador
@equipos.route('/lista-equipos')
@acceso_requerido(roles=["Administrador"])
@login_required
def lista_equipos():
    try:
        equipos = Equipo.query.all()
        return render_template('lista_equipos.html', equipos=equipos)
    except Exception as e:
        flash(_("Error al listar equipos: {}").format(e), "error")
        return redirect(url_for('equipos.lista_equipos'))

# Ruta para listar los equipos por agente
@equipos.route('/lista-equipos-agente')
@acceso_requerido(roles=["Agente"])
@login_required
def lista_equipos_agente():
    try:
        equipos = Equipo.query.all()
        return render_template('lista_equipos_agente.html', equipos=equipos)
    except Exception as e:
        flash(_("Error al listar equipos {}").format(e), "error")
        return redirect(url_for('equipos.lista_equipos_agente'))

# Ruta para actualizar un equipo
@equipos.route('/editar-equipo/<equipo_id>', methods=['GET', 'POST'])
@acceso_requerido(roles=["Administrador","Agente"])
@login_required
def editar_equipo(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)
    
    # Garantizar que imagenes sea lista antes de cargar el formulario
    if equipo.imagenes is None:
        equipo.imagenes = []
        
    form_edit_equipo = EditEquipoForm(obj=equipo)

    # Preparar entradas del formulario
    current_images_count = len(equipo.imagenes)
    while len(form_edit_equipo.imagenes.entries) < form_edit_equipo.imagenes.max_entries:
        form_edit_equipo.imagenes.append_entry()

    if form_edit_equipo.validate_on_submit():
        try:
            # 1. Evitar que populate_obj rompa si el formulario envía datos nulos
            form_edit_equipo.populate_obj(equipo)

            nuevas_imagenes = []
            # 2. SEGURO: Usar una copia local para la comparación de índices
            fotos_previas = equipo.imagenes if equipo.imagenes is not None else []

            # 3. Iterar sobre los campos del formulario de forma segura
            for imagen_field in form_edit_equipo.imagenes:
                # Si hay un archivo nuevo cargado
                if imagen_field.data and hasattr(imagen_field.data, 'filename') and imagen_field.data.filename:
                    filename = secure_filename(imagen_field.data.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join('app/static/img', unique_filename)
                    
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    imagen_field.data.save(file_path)
                    nuevas_imagenes.append(unique_filename)
                else:
                    # Si no hay archivo nuevo, intentar mantener la imagen anterior
                    idx = len(nuevas_imagenes)
                    if idx < len(fotos_previas):
                        # Solo añadir si el valor previo no es None
                        if fotos_previas[idx] is not None:
                            nuevas_imagenes.append(fotos_previas[idx])

            # 4. Actualizar el objeto con la nueva lista (limpia de Nones)
            equipo.imagenes = nuevas_imagenes
            
            equipo.actualizar_estado()
            equipo.usuario_id = current_user.id
            
            db.session.commit()
            
            # 5. Manejo seguro de funciones adicionales
            try:
                limpiar_imagenes_huerfanas()
            except:
                pass # Que no detenga el éxito del guardado principal

            flash("Equipo actualizado exitosamente", "success")
            
            # Redirección
            dest = 'equipos.lista_equipos' if current_user.rol.value == "Administrador" else 'equipos.lista_equipos_agente'
            return redirect(url_for(dest))

        except Exception as e:
            db.session.rollback()
            # Imprime el error en consola para ver exactamente qué falló (opcional)
            print(f"Error detallado: {e}") 
            flash(f"Error al actualizar: {e}", "error")
            return redirect(url_for('equipos.editar_equipo', equipo_id=equipo_id))
        
    return render_template('editar_equipo.html', form=form_edit_equipo, equipo=equipo, enumerate=enumerate, labels=labels)

    
@equipos.route('/eleminar-equipo/<equipo_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def eliminar_equipo(equipo_id):
   equipo = Equipo.query.get_or_404(equipo_id)
   try:
       if equipo:              
           db.session.delete(equipo)
           db.session.commit()
           flash(_("Equipo Eliminado con exito"), "success")
           limpiar_imagenes_huerfanas()
       else:
           flash(_("Equipo no encontrado"), "error")
   except Exception as e:
        db.session.rollback()
        flash(_("Error al eliminar el equipo: {}").format(e), "error")
   
   return redirect(url_for('equipos.lista_equipos'))
   

# Eliminación de imagenes huerfanas
def limpiar_imagenes_huerfanas():
    img_d_ruta = 'app/static/img'
     # Obtener todas las imágenes asociadas a los registros en la base de datos
    imagenes_en_bd = Equipo.query.with_entities(Equipo.imagenes).all()
     # Crear un conjunto de todas las imágenes en la base de datos
    imagenes_en_bd_set = set()
    for imagenes in imagenes_en_bd:
        # Asumiendo que imagenes esta en una lista 
        imagenes_en_bd_set.update(imagenes[0])
    # Listar todas las imágenes en el directorio    
    for img in os.listdir(img_d_ruta):
        if img not in imagenes_en_bd_set:
            try:
                os.remove(os.path.join(img_d_ruta, img))
                print(f"Imagenes huerfanas eliminadas: {img}")
            except Exception as e:
                print(f"Error al eliminar la imagen {img}:", e)
                
