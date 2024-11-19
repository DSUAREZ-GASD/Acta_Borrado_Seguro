from . import representantes
from flask import render_template, redirect, flash
from .forms import Nuevo_Representante, EditRespresentanteForm
import app #se llama al modelo
import os
from werkzeug.utils import secure_filename
from app.auth.routes import acceso_requerido
from flask_login import login_required

# Registro de firma
@representantes.route('/insertar', methods=['GET', 'POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def registro_representante():
    r = app.models.Representante()
    form = Nuevo_Representante()
    
    if form.validate_on_submit():
        # Poblar el objeto Firma
        form.populate_obj(r)
        r.firma = form.firma.data.filename
        app.db.session.add(r)
        app.db.session.commit()
        
        # Guardar cada imagen
        file = form.firma.data
        file.save(os.path.abspath(os.getcwd()+'/app/static/firmas/'+r.firma))
        flash("Registro de firmas exitoso")
        return redirect('/representantes/lista_representantes')
        
    return render_template('ingreso_representante.html', form=form)


@representantes.route('/lista_representantes')
@acceso_requerido(roles=["Administrador"])
@login_required
def lista_representantes():
    representantes = app.models.Representante.query.all()
    return render_template('lista_representante.html', representantes=representantes)


@representantes.route('/editar/<representante_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def editar(representante_id):
    # Seleccionar el firma con el Id
    r = app.models.Representante.query.get(representante_id) 
    if r is None:
        flash('El representante no existe')
        return redirect('/representantes/lista_representantes')
        
    # Cargo el formulario con los atributos del firma
    form_edit = EditRespresentanteForm(obj=r)
    
    current_firma = r.firma
    
    if form_edit.validate_on_submit():
        form_edit.populate_obj(r)
        
        if form_edit.firma.data and hasattr(form_edit.firma.data, 'filename'):
            filename = secure_filename(form_edit.firma.data.filename)  
            ruta_path = os.path.join('app/static/firmas', filename)
            form_edit.firma.data.save(ruta_path)
            r.firma = filename
        else:
            r.firma = current_firma
                               
        app.db.session.commit()
        flash("Representante actualizado con éxito")
        return redirect('/representantes/lista_representantes')
    else:
        if form_edit.errors:
            print("Formulario no valido")
            print(form_edit.errors)
                  
    return render_template('editar_representante.html', form=form_edit, representante=r)
                         
    
   # return "EL firma id editar:"+ representante_id
   
   
@representantes.route('/eliminar/<representante_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def eliminar(representante_id):
    r = app.models.Representante.query.get(representante_id)
    
    if r:
        app.db.session.delete(r)
        app.db.session.commit()
        
        print("Firma eliminada")
        flash("Firma eliminada con éxito")
        
        limpiar_firmas()
    else:
        flash('El representante no existe')
        
    return redirect('/representantes/lista_representantes')
    
# Eliminación de firmas huerfanas   
def limpiar_firmas():
    ruta_firma = 'app/static/firmas'
    
     # Obtener todas las firmas asociadas a los registros en la base de datos
    firmas_en_bd = app.models.Representante.query.with_entities(app.models.Representante.firma).all()
    
     # Crear un conjunto de todas las firmas en la base de datos
    firmas_en_bd_set = set()
    for firma in firmas_en_bd:
        # Asumiendo que firma esta en una lista 
        firmas_en_bd_set.update(firma)
    
    # Listar todas las firmas en el directorio    
    for fir in os.listdir(ruta_firma):
        if fir not in firmas_en_bd_set:
            try:
                os.remove(os.path.join(ruta_firma, fir))
                print(f"Firma eliminada: {fir}")
            except Exception as e:
                print(f"Error al eliminar la imagen {fir}:", e)  