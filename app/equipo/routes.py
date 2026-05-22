from flask import render_template, redirect, flash, url_for
from flask_login import login_required, current_user
from flask_babel import _ # type: ignore
from . import equipos
from app import db
from app.auth.routes import acceso_requerido
from app.models import Equipo
from .forms import NuevoEquipo, EditEquipoForm
from app.utils import guardar_imagen_estandarizada, limpiar_imagenes_huerfanas

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

# ==========================================
# RUTA: CREAR EQUIPO
# ==========================================
@equipos.route('/crear', methods=["GET", "POST"])
# Permitimos la entrada a Admins, Operadores (Agente 1) y Supervisores (Agente 2)
@acceso_requerido(roles=["Administrador", "Agente_1", "Agente_2"])
@login_required
def crear():
    form = NuevoEquipo()
    
    if not current_user.tiene_permiso("subir_imagenes"):
        flash(_("Tu perfil no cuenta con permisos para registrar nuevos equipos."), "error")
        return redirect(url_for('auth.login'))
    
    if form.validate_on_submit():
        try:
            equipo = Equipo()
            form.populate_obj(equipo)
            equipo.usuario_id = current_user.id
            
            # Procesar imágenes: Filtra solo las que tienen datos
            equipo.imagenes = [
                guardar_imagen_estandarizada(f.data, subfolder='equipos') 
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

# ==========================================
# RUTA: LISTAR EQUIPOS (ADMINISTRADOR)
# ==========================================
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

# ==========================================
# RUTA: LISTAR EQUIPOS (AGENTES OPERATIVOS)
# ==========================================
@equipos.route('/lista-agente')
@acceso_requerido(roles=["Agente_1", "Agente_2"])
@login_required
def lista_equipos_agente():
    try:
        lista_de_equipos = Equipo.query.all()
        return render_template('equipo/lista_agente.html', equipos=lista_de_equipos)
    except Exception as e:
        flash(_("Error al listar equipos {}").format(e), "error")
        return redirect(url_for('auth.login'))
    
# ==========================================
# RUTA: LISTAR EQUIPOS (AGENTES AUDITORES)
# ==========================================
@equipos.route('/lista-auditor')
@acceso_requerido(roles=["Agente_3"])
@login_required
def lista_equipos_auditor():
    try:
        lista_de_equipos = Equipo.query.all()
        return render_template('equipo/lista_auditor.html', equipos=lista_de_equipos)
    except Exception as e:
        flash(_("Error al listar equipos {}").format(e), "error")
        return redirect(url_for('auth.login'))

# ==========================================
# RUTA: EDITAR / REEMPLAZAR IMÁGENES Y DATOS
# ==========================================
@equipos.route('/editar/<equipo_id>', methods=['GET', 'POST'])
@acceso_requerido(roles=["Administrador", "Agente_1", "Agente_2"])
@login_required
def editar(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)
    form = EditEquipoForm(obj=equipo)

    # Aseguramos que el FieldList de WTForms siempre tenga exactamente 8 entradas en memoria
    while len(form.imagenes.entries) < form.imagenes.max_entries:
        form.imagenes.append_entry()

    if form.validate_on_submit():
        try:
            # Aseguramos que fotos_previas sea una lista de 8 elementos (rellenando con None si es más corta)
            fotos_previas = equipo.imagenes if equipo.imagenes else []
            while len(fotos_previas) < 8:
                fotos_previas.append(None)
            
            nuevas_imagenes = []
            
            # --- VALIDACIÓN Y RECONSTRUCCIÓN EN UN SOLO PASO EN BASE A LA REALIDAD DE LA BD ---
            for i in range(8):
                campo_imagen = form.imagenes[i]
                foto_antigua = fotos_previas[i]
                
                # Intentamos procesar el archivo si el usuario subió algo en este slot
                # (WTForms a veces llena campo_imagen.data con un objeto de archivo vacío, por eso validamos el filename)
                tiene_archivo_nuevo = campo_imagen.data and hasattr(campo_imagen.data, 'filename') and campo_imagen.data.filename != ''
                
                if tiene_archivo_nuevo:
                    # CASO A: El slot YA tenía una foto registrada en la Base de Datos (Es un REEMPLAZO)
                    if foto_antigua:
                        if not current_user.tiene_permiso("reemplazar_imagenes"):
                            flash(_(f"Acción denegada: Tu perfil (Agente 1) no puede reemplazar la foto del slot {i+1}."), "error")
                            return redirect(url_for('equipo.editar', equipo_id=equipo_id))
                    
                    # CASO B: El slot estaba vacío (None) en la Base de Datos (Es una SUBIDA NUEVA)
                    else:
                        if not current_user.tiene_permiso("subir_imagenes"):
                            flash(_("Acción denegada: No tienes permisos para añadir nuevas imágenes."), "error")
                            return redirect(url_for('equipo.editar', equipo_id=equipo_id))
                    
                    # Si pasa los permisos correspondientes, guardamos el archivo físico
                    nombre_nuevo = guardar_imagen_estandarizada(campo_imagen.data, subfolder='equipos')
                    nuevas_imagenes.append(nombre_nuevo)
                
                else:
                    # El usuario NO subió ningún archivo nuevo en este slot específico
                    # Si ya había una foto antes, la conservamos intacta sin importar lo que diga WTForms
                    if foto_antigua:
                        nuevas_imagenes.append(foto_antigua)
                    else:
                        nuevas_imagenes.append(None)

            # Sincronizamos la lista de 8 elementos en la base de datos
            equipo.imagenes = nuevas_imagenes
            
            # --- ACTUALIZACIÓN DE DATOS DE TEXTO ---
            equipo.nombre = form.nombre.data
            # equipo.serial = form.serial.data (Mapea aquí tus otros inputs de texto)

            equipo.usuario_id = current_user.id
            equipo.actualizar_estado()
            
            db.session.commit()
            try: limpiar_imagenes_huerfanas()
            except: pass

            flash(_("Equipo actualizado con éxito"), "success")
            dest = 'equipo.lista_equipos' if current_user.rol.value == "Administrador" else 'equipo.lista_equipos_agente'
            return redirect(url_for(dest))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {e}", "error")
            return redirect(url_for('equipo.editar', equipo_id=equipo_id))
        
    return render_template('equipo/editar.html', form=form, equipo=equipo, labels=labels)


# ==========================================
# RUTA: ELIMINAR EQUIPO
# ==========================================
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