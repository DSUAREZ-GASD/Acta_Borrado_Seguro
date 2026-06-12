from flask import render_template, redirect, flash, url_for, request
from flask_login import login_required, current_user
from flask_babel import _
from . import acta_verificacion
from app import db
from app.models import Actividad_verificacion
from app.utils import acceso_requerido
from app.utils.imagenes import guardar_imagen_estandarizada
from .forms import GestionarEvidenciasForm

labels = [
    "Foto de la caja del equipo",
    "Foto del equipo",
    "Foto serial del equipo",
    "Foto de la Identificación de la comisión",
    "Foto inicio de generación de la imagen",
    "Foto finalización de la generación de la imagen",
    "Foto inicio del borrado",
]


def _obtener_listado_por_rol():
    rol_actual = current_user.rol.value if hasattr(current_user.rol, 'value') else current_user.rol
    if rol_actual == 'Agente_3':
        return 'acta_verificacion.lista_auditor'
    return 'acta_verificacion.lista'


@acta_verificacion.route('/lista')
@acceso_requerido(roles=["Administrador"])
@login_required
def lista():
    actividades = Actividad_verificacion.query.filter_by(activo=True).all()
    return render_template('acta_verificacion/lista.html', actividades=actividades)


@acta_verificacion.route('/lista-auditor')
@acceso_requerido(roles=["Agente_3"])
@login_required
def lista_auditor():
    actividades = Actividad_verificacion.query.filter_by(activo=True).all()
    return render_template('acta_verificacion/lista_auditor.html', actividades=actividades)


@acta_verificacion.route('/gestionar-evidencias/<int:actividad_id>', methods=['GET', 'POST'])
@acceso_requerido(roles=["Administrador", "Agente_3"])
@login_required
def gestionar_evidencias(actividad_id):
    actividad = Actividad_verificacion.query.get_or_404(actividad_id)
    form = GestionarEvidenciasForm()

    if request.method == 'GET':
        while len(form.evidencias.entries) < 7:
            form.evidencias.append_entry()

    if form.validate_on_submit():
        try:
            evidencias = []
            for i in range(7):
                campo = form.evidencias[i]
                if campo.data and hasattr(campo.data, 'filename') and campo.data.filename:
                    nombre_archivo = guardar_imagen_estandarizada(campo.data, subfolder='verificaciones')
                    evidencias.append(nombre_archivo)
                else:
                    anterior = actividad.evidencias[i] if actividad.evidencias and i < len(actividad.evidencias) else None
                    evidencias.append(anterior)

            actividad.evidencias = evidencias
            db.session.commit()
            flash(_("Evidencias guardadas correctamente."), "success")
            return redirect(url_for(_obtener_listado_por_rol()))
        except Exception as e:
            db.session.rollback()
            flash(_("Error al guardar las evidencias: {}").format(e), "error")

    return render_template(
        'acta_verificacion/actividad.html',
        actividad=actividad,
        form=form,
        labels=labels,
    )


@acta_verificacion.route('/eliminar/<int:actividad_id>')
@acceso_requerido(roles=["Administrador"])
@login_required
def eliminar(actividad_id):
    actividad = Actividad_verificacion.query.get_or_404(actividad_id)
    try:
        actividad.activo = False
        db.session.commit()
        flash(_("Acta de verificación eliminada con éxito."), "success")
    except Exception as e:
        db.session.rollback()
        flash(_("No se pudo eliminar el acta: {}".format(e)), "error")
    return redirect(url_for('acta_verificacion.lista'))
