from flask import render_template, redirect, flash, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from flask_babel import _ # type: ignore
import os
import uuid
from . import equipos
from app import db
from app.auth.routes import acceso_requerido
from app.models import Equipo
from .forms import NuevoEquipo, EditEquipoForm
from PIL import Image as PILImage, ImageOps

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

STANDARD_SIZE = (1280, 720)

def guardar_imagen_estandarizada(file_storage, upload_folder='app/static/img'):
    if not (file_storage and hasattr(file_storage, 'filename') and file_storage.filename):
        return None
    
    temp_filename = f"{uuid.uuid4()}.jpg" 
    file_path = os.path.join(upload_folder, temp_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        img = PILImage.open(file_storage)

        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        img = ImageOps.exif_transpose(img)
        
        img_estandarizada = ImageOps.contain(img, STANDARD_SIZE, PILImage.Resampling.LANCZOS)

        img_estandarizada.save(file_path, quality=90, optimize=True)
        
        return temp_filename

    except Exception as e:
        print(f"Error procesando imagen: {e}")
        return None


# Ruta para crear un equipo
@equipos.route('/crear', methods=["GET", "POST"])
@acceso_requerido(roles=["Administrador", "Agente"])
@login_required
def crear():
    form = NuevoEquipo()
    if form.validate_on_submit():
        try:
            equipo = Equipo()
            form.populate_obj(equipo)
            equipo.usuario_id = current_user.id
            
            # Procesar imágenes: Filtra solo las que tienen datos
            equipo.imagenes = [
                guardar_imagen_estandarizada(f.data) 
                for f in form.imagenes if f.data
            ]

            db.session.add(equipo)
            db.session.commit()
            
            flash(_("Registro de equipo exitoso"), "success")
            dest = 'equipo.lista_equipos' if current_user.rol.value == "Administrador" else 'equipo.lista_equipos_agente'
            return redirect(url_for(dest))
            
        except Exception as e:
            db.session.rollback()
            flash(_(f"Error al registrar equipo: {e}"), "error")
            
    return render_template('equipo/crear.html', form=form, labels=labels)

# Ruta para listar los equipos por administrador
@equipos.route('/lista')
@acceso_requerido(roles=["Administrador"])
@login_required
def lista_equipos():
    try:
        lista_de_equipos = Equipo.query.all()
        return render_template('equipo/lista.html', equipos=lista_de_equipos)
    except Exception as e:
        flash(_("Error al listar equipos: {}").format(e), "error")
        return redirect(url_for('auth.login'))

# Ruta para listar los equipos por agente
@equipos.route('/lista-agente')
@acceso_requerido(roles=["Agente"])
@login_required
def lista_equipos_agente():
    try:
        lista_de_equipos = Equipo.query.all()
        return render_template('equipo/lista_agente.html', equipos=lista_de_equipos)
    except Exception as e:
        flash(_("Error al listar equipos {}").format(e), "error")
        return redirect(url_for('auth.login'))

# Ruta para actualizar un equipo
@equipos.route('/editar/<equipo_id>', methods=['GET', 'POST'])
@acceso_requerido(roles=["Administrador", "Agente"])
@login_required
def editar(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)
    form = EditEquipoForm(obj=equipo)

    # Rellenar entradas vacías para el formulario
    while len(form.imagenes.entries) < form.imagenes.max_entries:
        form.imagenes.append_entry()

    if form.validate_on_submit():
        try:
            # Respaldamos las fotos actuales antes de poblar el objeto
            fotos_previas = equipo.imagenes or []
            form.populate_obj(equipo)
            
            nuevas_imagenes = []
            for i, campo_imagen in enumerate(form.imagenes):
                # Si se subió un archivo nuevo, lo guardamos
                nombre_nuevo = guardar_imagen_estandarizada(campo_imagen.data)
                
                if nombre_nuevo:
                    nuevas_imagenes.append(nombre_nuevo)
                elif i < len(fotos_previas):
                    # Si no hay archivo nuevo, mantenemos la que estaba en esa posición
                    nuevas_imagenes.append(fotos_previas[i])

            equipo.imagenes = nuevas_imagenes
            equipo.usuario_id = current_user.id
            equipo.actualizar_estado()
            
            db.session.commit()
            
            # Limpieza silenciosa
            try: limpiar_imagenes_huerfanas() 
            except: pass

            flash("Equipo actualizado exitosamente", "success")
            dest = 'equipo.lista_equipos' if current_user.rol.value == "Administrador" else 'equipo.lista_equipos_agente'
            return redirect(url_for(dest))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {e}", "error")
            return redirect(url_for('equipos.editar', equipo_id=equipo_id))
        
    return render_template('equipo/editar.html', form=form, equipo=equipo, labels=labels)

    
@equipos.route('/eliminar/<equipo_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def eliminar(equipo_id):
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
   
   return redirect(url_for('equipo.lista_equipos'))
   

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
                
