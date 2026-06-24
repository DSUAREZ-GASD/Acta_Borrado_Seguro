from flask import render_template, redirect, flash, url_for, request
from flask_login import login_required, current_user
from flask_babel import gettext as _ # <-- Ajustado para consistencia
from . import equipos
from app import db
from app.models import Actividad_verificacion, Equipo, EstadoEnum
from .forms import NuevoEquipo, EditEquipoForm
from app.utils import guardar_imagen_estandarizada, evaluar_estado_equipo, limpiar_imagenes_huerfanas, acceso_requerido, usuario_debe_bloquear_maestro


def redireccionar_flujo_equipo(equipo):
    """
    Evalúa el rol institucional y el tipo de dispositivo para despachar al operador
    a la lista de equipos correspondiente, inyectando un mensaje de éxito adaptativo.
    """
    rol_actual = current_user.rol.value if hasattr(current_user.rol, 'value') else current_user.rol
    
    if equipo.es_verificacion:
        flash(_("Equipo registrado con éxito y habilitado para el flujo de Verificación Técnica de Laboratorio."), "success")
    else:
        flash(_("Equipo de borrado seguro registrado y procesado correctamente en el sistema."), "success")

    if rol_actual == "Administrador":
        return redirect(url_for('equipo.lista_equipos'))
    elif rol_actual == "Agente_3":
        return redirect(url_for('equipo.lista_equipos_auditor'))
    else:
        return redirect(url_for('equipo.lista_equipos_agente'))


def sincronizar_acta_verificacion(equipo):
    """Garantiza la relación 1:1 entre Equipo y Actividad_verificacion."""
    if equipo.es_verificacion:
        if not equipo.actividad_asociada:
            acta = Actividad_verificacion(equipo=equipo, evidencias=[None] * 7)
            db.session.add(acta)
        elif not equipo.actividad_asociada.activo:
            equipo.actividad_asociada.activo = True
    else:
        if equipo.actividad_asociada and equipo.actividad_asociada.activo:
            equipo.actividad_asociada.activo = False
    
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
@acceso_requerido(roles=["Administrador", "Agente_1", "Agente_2", "Agente_3"])
@login_required
def crear():
    form = NuevoEquipo() 
    
    if not current_user.tiene_permiso("subir_imagenes"):
        flash(_("Tu perfil no cuenta con permisos para registrar nuevos equipos."), "error")
        return redirect(url_for('auth.login'))
        
    # Extracción segura del valor del rol (Solución al Enum)
    rol_actual = current_user.rol.value if hasattr(current_user.rol, 'value') else current_user.rol
    es_agente_restringido = rol_actual in ["Agente_1", "Agente_2"]
    
    if es_agente_restringido:
        form.es_maestro.render_kw = {'disabled': 'disabled', 'class': 'form-control bg-light'}
        form.es_verificacion.render_kw = {'disabled': 'disabled', 'class': 'form-control bg-light'}
        if hasattr(form, 'confirmar_log'):
            form.confirmar_log.render_kw = {'disabled': 'disabled', 'class': 'form-check-input'}
    
    if form.validate_on_submit():
        try:
            equipo = Equipo()
            form.populate_obj(equipo)
            equipo.usuario_id = current_user.id
            
            if es_agente_restringido:
                equipo.es_maestro = False
                equipo.es_verificacion = False
            else:
                equipo.es_maestro = form.es_maestro.data
                equipo.es_verificacion = form.es_verificacion.data
                
                if hasattr(form, 'confirmar_log') and form.confirmar_log.data:
                    nota_log = "[LOG VERIFICADO Y VALIDADO CON ÉXITO]"
                    equipo.observacion = f"{equipo.observacion or ''} {nota_log}".strip()
            
            lista_imagenes = []
            for i in range(8):
                campo_imagen = form.imagenes[i] if i < len(form.imagenes.entries) else None
                if campo_imagen and campo_imagen.data and hasattr(campo_imagen.data, 'filename') and campo_imagen.data.filename != '':
                    meta = {
                        'departamento': equipo.departamento,
                        'municipio': equipo.municipio,
                        'comision': equipo.cod_comision or equipo.comision,
                        'equipo': equipo.nombre,
                    }
                    nombre_foto = guardar_imagen_estandarizada(campo_imagen.data, subfolder='equipos', meta=meta, slot=i)
                    lista_imagenes.append(nombre_foto)
                else:
                    lista_imagenes.append(None)
            equipo.imagenes = lista_imagenes

            nuevo_estado, mensaje_flujo = evaluar_estado_equipo(equipo)
            equipo.estado = nuevo_estado
            equipo.actualizar_estado()
            
            db.session.add(equipo)
            sincronizar_acta_verificacion(equipo)
            db.session.commit()
            
            if equipo.estado in [EstadoEnum.PENDIENTE_HASH, EstadoEnum.PENDIENTE_LOG]:
                flash(_(mensaje_flujo), "warning")
            elif equipo.estado == EstadoEnum.FINALIZADO:
                flash(_(mensaje_flujo), "success")
            else:
                flash(_(mensaje_flujo), "info")
                
            return redireccionar_flujo_equipo(equipo)
            
        except Exception as e:
            db.session.rollback()
            flash(_(f"Error al registrar equipo: {e}"), "error")
            
    if form.errors:
        print("!!! ERRORES DE VALIDACIÓN EN CREAR:", form.errors)
        flash(_("El formulario tiene errores de validación: {}").format(form.errors), "error")
    
    return render_template('equipo/crear.html', form=form, labels=labels, es_agente_restringido=es_agente_restringido)
    return render_template('equipo/crear.html', form=form, labels=labels, es_agente_restringido=es_agente_restringido)

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
# ==========================================
# RUTA: EDITAR EQUIPO
# ==========================================
@equipos.route('/editar/<equipo_id>', methods=['GET', 'POST'])
@acceso_requerido(roles=["Administrador", "Agente_1", "Agente_2", "Agente_3"])
@login_required
def editar(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)
    form = EditEquipoForm(obj=equipo)
    
    nota_log = "[LOG VERIFICADO Y VALIDADO CON ÉXITO]"
    
    if request.method == 'GET':
        form.confirmar_log.data = bool(equipo.observacion and nota_log in equipo.observacion)
            
    bloquear_campos = usuario_debe_bloquear_maestro(current_user, equipo)
    # Extracción segura del valor del rol
    rol_actual = current_user.rol.value if hasattr(current_user.rol, 'value') else current_user.rol
    es_agente_restringido = rol_actual in ["Agente_1", "Agente_2"]

    campos_texto = [
        'direccion', 'comision', 'cod_comision', 'capacidad', 'municipio', 
        'departamento', 'equipo_marca', 'equipo_modelo', 'equipo_serial', 
        'dd_marca', 'dd_modelo', 'dd_serial', 'sha_1', 'md5', 'proceso'
    ]
    campos_booleanos = ['es_maestro', 'es_verificacion', 'confirmar_log']

    if bloquear_campos or es_agente_restringido:
        for nombre_campo in campos_texto:
            if nombre_campo in form:
                form[nombre_campo].render_kw = {'readonly': True, 'class': 'form-control bg-light'}
        
        for nombre_campo in campos_booleanos:
            if nombre_campo in form:
                form[nombre_campo].render_kw = {'disabled': 'disabled'}

    if len(form.imagenes.entries) < form.imagenes.max_entries:
        form.imagenes.append_entry()

    if form.validate_on_submit():
        try:
            respaldo_maestro = equipo.es_maestro
            respaldo_verificacion = equipo.es_verificacion
            respaldo_confirmar_log = bool(equipo.observacion and nota_log in equipo.observacion)
            
            form.populate_obj(equipo)
            
            if bloquear_campos or es_agente_restringido:
                equipo.es_maestro = respaldo_maestro
                equipo.es_verificacion = respaldo_verificacion
                
                if respaldo_confirmar_log and (not equipo.observacion or nota_log not in equipo.observacion):
                    equipo.observacion = f"{equipo.observacion or ''} {nota_log}".strip()
            else:
                equipo.es_maestro = form.es_maestro.data
                equipo.es_verificacion = form.es_verificacion.data

                if hasattr(form, 'confirmar_log') and form.confirmar_log.data:
                    if not equipo.observacion or nota_log not in equipo.observacion:
                        equipo.observacion = f"{equipo.observacion or ''} {nota_log}".strip()
                elif hasattr(form, 'confirmar_log') and not form.confirmar_log.data:
                    if equipo.observacion and nota_log in equipo.observacion:
                        equipo.observacion = equipo.observacion.replace(nota_log, "").strip()

            fotos_previas = equipo.imagenes if equipo.imagenes else [None] * 8
            nuevas_imagenes = []
            
            for i in range(8):
                campo_imagen = form.imagenes[i]
                foto_antigua = fotos_previas[i] if i < len(fotos_previas) else None
                tiene_archivo_nuevo = campo_imagen.data and hasattr(campo_imagen.data, 'filename') and campo_imagen.data.filename != ''
                
                if tiene_archivo_nuevo:
                    if equipo.es_maestro and i in [6, 7]:
                        flash(_("Acción bloqueada: Los equipos maestros no permiten imágenes de borrado."), "error")
                        return redirect(url_for('equipo.editar', equipo_id=equipo_id))
                        
                    meta = {
                        'departamento': equipo.departamento,
                        'municipio': equipo.municipio,
                        'comision': equipo.cod_comision or equipo.comision,
                        'equipo': equipo.nombre,
                    }
                    nombre_nuevo = guardar_imagen_estandarizada(campo_imagen.data, subfolder='equipos', meta=meta, slot=i)
                    nuevas_imagenes.append(nombre_nuevo)
                else:
                    nuevas_imagenes.append(foto_antigua)
            
            equipo.imagenes = nuevas_imagenes

            nuevo_estado, mensaje_flujo = evaluar_estado_equipo(equipo)
            equipo.estado = nuevo_estado
            equipo.actualizar_estado()  
            sincronizar_acta_verificacion(equipo)
            db.session.commit()
            
            if equipo.estado in [EstadoEnum.PENDIENTE_HASH, EstadoEnum.PENDIENTE_LOG]:
                flash(_(mensaje_flujo), "warning")
            elif equipo.estado == EstadoEnum.FINALIZADO:
                flash(_(mensaje_flujo), "success")
            else:
                flash(_(mensaje_flujo), "info")

            return redireccionar_flujo_equipo(equipo)

        except Exception as e:
            db.session.rollback()
            flash(f"Error de consistencia: {e}", "error")
            return redirect(url_for('equipo.editar', equipo_id=equipo_id))
        
    return render_template(
        'equipo/editar.html', 
        form=form, 
        equipo=equipo, 
        labels=labels, 
        bloquear_campos=bloquear_campos,
        es_agente_restringido=es_agente_restringido
    )

# ==========================================
# RUTA: ELIMINAR EQUIPO
# ==========================================
@equipos.route('/eliminar/<equipo_id>', methods=['GET','POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def eliminar(equipo_id):
<<<<<<< Updated upstream
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
=======
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

# ==========================================
# RUTA: IMPORTAR EQUIPOS DESDE CSV
# ==========================================
@equipos.route('/importar', methods=['GET', 'POST'])
@acceso_requerido(roles=["Administrador"])
@login_required
def importar_csv():
    if request.method == 'POST':
        archivo = request.files.get('archivo_csv')
        
        if not archivo or archivo.filename == '':
            flash(_("No se seleccionó ningún archivo."), "error")
            return redirect(url_for('equipo.importar_csv'))
            
        if not archivo.filename.endswith('.csv'):
            flash(_("El archivo debe ser en formato CSV."), "error")
            return redirect(url_for('equipo.importar_csv'))

        try:
            contenido = archivo.stream.read().decode("UTF-8-sig")
            stream = io.StringIO(contenido, newline=None)
            
            primera_linea = contenido.split('\n')[0]
            if '\t' in primera_linea:
                delimitador = '\t'
            elif ';' in primera_linea:
                delimitador = ';'
            else:
                delimitador = ','
            
            csv_input = csv.DictReader(stream, delimiter=delimitador)
            
            if csv_input.fieldnames:
                csv_input.fieldnames = [str(campo).strip().lower() for campo in csv_input.fieldnames]
            
            registros_exitosos = 0
            
            for fila in csv_input:
                serial_csv = fila.get('serial', '').strip()
                
                if not serial_csv:
                    continue
                
                marca_csv = fila.get('marca', '').strip()
                modelo_csv = fila.get('modelo', '').strip()
                nombre_csv = fila.get('nombre', '').strip()
                
                if not nombre_csv:
                    if marca_csv or modelo_csv:
                        nombre_csv = f"{marca_csv} {modelo_csv}".strip()
                    else:
                        nombre_csv = f"Equipo {serial_csv}"
                
                tipo_disco_csv = fila.get('tipo_disco', '').strip()
                comision_csv = fila.get('comision', '').strip()
                municipio_csv = fila.get('municipio', '').strip()
                departamento_csv = fila.get('departamento', '').strip()
                
                str_maestro = fila.get('es_maestro', '0').strip().lower()
                es_maestro_bool = True if str_maestro in ['1', 'true', 'si', 's'] else False
                
                str_verificacion = fila.get('es_verificacion', '0').strip().lower()
                es_verificacion_bool = True if str_verificacion in ['1', 'true', 'si', 's'] else False

                nuevo_equipo = Equipo(
                    nombre=nombre_csv,
                    equipo_serial=serial_csv,
                    equipo_marca=marca_csv,
                    equipo_modelo=modelo_csv,
                    dd_modelo=tipo_disco_csv, 
                    comision=comision_csv,
                    municipio=municipio_csv,
                    departamento=departamento_csv,
                    es_maestro=es_maestro_bool,
                    es_verificacion=es_verificacion_bool,
                    usuario_id=current_user.id
                )
                
                nuevo_estado, mensaje_ignorado = evaluar_estado_equipo(nuevo_equipo)
                nuevo_equipo.estado = nuevo_estado
                
                db.session.add(nuevo_equipo)
                registros_exitosos += 1
                
            db.session.commit()
            flash(_("Se importaron {} equipos correctamente.").format(registros_exitosos), "success")
            return redirect(url_for('equipo.lista_equipos'))
            
        except UnicodeDecodeError:
            db.session.rollback()
            flash(_("Error de codificación. Asegúrate de guardar el CSV con formato UTF-8."), "error")
            return redirect(url_for('equipo.importar_csv'))
        except Exception as e:
            db.session.rollback()
            flash(_("Error al procesar el archivo: {}").format(e), "error")
            return redirect(url_for('equipo.importar_csv'))

    return render_template('equipo/importar_csv.html')
>>>>>>> Stashed changes
