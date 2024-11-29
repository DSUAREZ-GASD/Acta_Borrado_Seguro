from flask import render_template, redirect, flash, url_for
from werkzeug.utils import secure_filename
from flask_babel import _
import os
from . import representantes
from app import db
from app.auth.routes import acceso_requerido
from app.models import Representante
from .forms import Nuevo_Representante, EditRespresentanteForm


from flask_login import login_required

# Registro de representantes
@representantes.route('/registro-representante', methods=['GET', 'POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def registro_representante():
    representante = Representante()
    form = Nuevo_Representante()
    
    if form.validate_on_submit():
        try:
            form.populate_obj(representante)
            representante.firma = secure_filename(form.firma.data.filename)
            db.session.add(representante)
            db.session.commit()
            
            file = form.firma.data
            file.save(os.path.join('app','static','firmas', representante.firma))
            flash(_("Registro de representante exitoso"), "success")
            return redirect(url_for('representantes.lista_representantes'))
        except Exception as e:
            db.session.rollback()
            flash(_("Error al registrar la firma: ").format(e), "error")
        
    return render_template('registro_representante.html', form=form)

# Listado de representantes
@representantes.route('/lista-representantes')
@acceso_requerido(roles=["Administrador"])
@login_required
def lista_representantes():
    try:
        representantes = Representante.query.all()
        return render_template('lista_representantes.html', representantes=representantes)
    except Exception as e:
        flash(_("Error al cargar la lista de representantes: ")+format(e), "error")
        return redirect(url_for('representantes.lista_representantes'))

# Edición de representantes
@representantes.route('/editar-representante/<representante_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def editar_representante(representante_id):
    representante = Representante.query.get_or_404(representante_id) 
    if representante is None:
        flash(_("El representante no existe"), "error")
        return redirect(url_for('representantes.lista_representantes'))
        
    form_edit = EditRespresentanteForm(obj=representante)
    current_firma = representante.firma
    
    if form_edit.validate_on_submit():
        try:
            form_edit.populate_obj(representante)
            
            if form_edit.firma.data and hasattr(form_edit.firma.data, 'filename'):
                filename = secure_filename(form_edit.firma.data.filename)  
                ruta_path = os.path.join('app','static','firmas', filename)
                form_edit.firma.data.save(ruta_path)
                representante.firma = filename
            else:
                representante.firma = current_firma
                                
            db.session.commit()
            flash(_("Representante actualizado con éxito"), "success")
            limpiar_firmas()
            return redirect(url_for('representantes.lista_representantes'))
        except Exception as e:
            db.session.rollback()
            flash(_("Error al actualizar el representante: ").format(e), "error")
                  
    return render_template('editar_representante.html', form=form_edit, representante=representante)             
   
# Eliminación de representantes
@representantes.route('/eliminar-representante/<representante_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def eliminar_representante(representante_id):
    representante = Representante.query.get_or_404(representante_id)
    try:
        if representante:
            db.session.delete(representante)
            db.session.commit()
            flash(_("Representante eliminado con éxito"), "success")
            limpiar_firmas()
    except Exception as e:
        db.session.rollback()
        flash(("Error al eliminar el representante: ").format(e), "error")
        return redirect(url_for('representantes.lista_representantes'))
    
    return redirect(url_for('representantes.lista_representantes'))
    
# Eliminación de firmas huerfanas   
def limpiar_firmas():
    ruta_firma = os.path.join('app','static','firmas')
    firmas_en_bd = {firma for (firma,) in Representante.query.with_entities(Representante.firma).all()}
     
    for fir in os.listdir(ruta_firma):
        if fir not in firmas_en_bd:
            try:
                os.remove(os.path.join(ruta_firma, fir))
                print(f"Firma eliminada: {fir}")
            except Exception as e:
                print(f"Error al eliminar la imagen {fir}:", {e.strerror})  