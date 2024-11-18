from app.auth.routes import acceso_requerido
from . import equipos
#el . es para que nos importe todo el modulo
from flask import render_template, redirect, flash
from .forms import NuevoEquipo,EditEquipoForm
import app#se llama al modelo
import os 
from werkzeug.utils import secure_filename
from flask_login import current_user

@equipos.route('/crear', methods=["GET","POST"])
@acceso_requerido(roles=["Administrador","Agente"])
def crear_Equipo():
    e = app.models.Equipo()
    form = NuevoEquipo()
    
    if form.validate_on_submit():
        # Poblar el objeto Producto
        form.populate_obj(e)
        e.imagenes = []

        # Guardar cada imagen
        for imagen_field in form.imagenes:
            if imagen_field.data:
                filename = imagen_field.data.filename
                # Guardar la imagen en el sistema de archivos
                imagen_field.data.save(os.path.join('app/static/imagenes', filename))
                # Agregar el nombre de la imagen a la lista
                e.imagenes.append(filename)

        # Agregar el producto a la base de datos
        app.db.session.add(e)
        app.db.session.commit()
        if current_user.rol.value == "Administrador":
            flash("Registro de equipo exitoso")
            return redirect('/equipos/listar')
        elif current_user.rol.value == "Agente":
            flash("Registro de equipo exitoso")
            return redirect('/equipos/lista_agente')
        else:
            flash("Error al registrar equipo")
    
    return render_template('registro.html', form=form)


@equipos.route('/listar')
@acceso_requerido(roles=["Administrador"])
def listar():
   #Traeremos los equipos  de la base de datos
   equipos = app.Equipo.query.all()
   #mostrar la vista de listar
   #envieandole los equipos seleccionados
   return render_template('listar.html',
                          equipos=equipos)
   
@equipos.route('/lista_agente')
@acceso_requerido(roles=["Agente"])
def lista_agente():
    #Traeremos los equipos  de la base de datos
    equipos = app.models.Equipo.query.all()
    #mostrar la vista de listar
    return render_template('listar_agente.html',
                            equipos=equipos)
   
@equipos.route('/editar/<equipo_id>', methods=['GET', 'POST'])
@acceso_requerido(roles=["Administrador","Agente"])
def editar(equipo_id):
    e = app.models.Equipo.query.get(equipo_id)
    form_edit = EditEquipoForm(obj=e)

    # Cargar las imágenes actuales del equipo en el formulario
    current_images_count = len(e.imagenes)
    
    # Solo agregar entradas si hay menos de max_entries
    while len(form_edit.imagenes.entries) < form_edit.imagenes.max_entries:
        form_edit.imagenes.append_entry()

    if form_edit.validate_on_submit():
        print("Formulario validado correctamente")
        form_edit.populate_obj(e)

        nuevas_imagenes = []

        # Guardar nuevas imágenes
        for imagen_field in form_edit.imagenes:
            if imagen_field.data and hasattr(imagen_field.data, 'filename') and imagen_field.data.filename:
                filename = secure_filename(imagen_field.data.filename)
                file_path = os.path.join('app/static/imagenes', filename)
                imagen_field.data.save(file_path)
                nuevas_imagenes.append(filename)
            else:
                # Si no se ha subido una nueva imagen, mantener la imagen actual
                index = len(nuevas_imagenes)
                if index < current_images_count:
                    nuevas_imagenes.append(e.imagenes[index])

        # Actualizar las imágenes en la base de datos
        e.imagenes = nuevas_imagenes
        # Actualizar el estado y la fecha de finalización
        e.actualizar_estado()
        app.db.session.commit()
        if current_user.rol.value == "Administrador":
            flash("Registro de equipo exitoso")
            return redirect('/equipos/listar')
        elif current_user.rol.value == "Agente":
            flash("Registro de equipo exitoso")
            return redirect('/equipos/lista_agente')
        else:
            flash("Error al registrar equipo")
    else:
        if form_edit.errors:
            print("Formulario no validado")
            print(form_edit.errors)
            

    return render_template('editar.html', form=form_edit, equipo=e, enumerate=enumerate)
  
    
@equipos.route('/eleminar/<equipo_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
def eliminar(equipo_id):
   # Seleccionar producto con el Id
   e = app.models.Equipo.query.get(equipo_id)
   
   # Condición para borrar las imagenes de equipo
   if e:
       # Eliminar el registro del equipo de la base de datos
       app.db.session.delete(e)
       app.db.session.commit()
       print("Imagenes eliminadas")
       flash("Equipo Eliminado con exito")
       
       limpiar_imagenes_huerfanas()
   else:
       flash("Equipo no encontrado")
   
   return redirect('/equipos/listar')
   

# Eliminación de imagenes huerfanas
def limpiar_imagenes_huerfanas():
    img_d_ruta = 'app/static/imagenes'
    
     # Obtener todas las imágenes asociadas a los registros en la base de datos
    imagenes_en_bd = app.models.Equipo.query.with_entities(app.models.Equipo.imagenes).all()
    
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