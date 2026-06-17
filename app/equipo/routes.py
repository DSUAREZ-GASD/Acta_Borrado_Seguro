import csv
import io
from flask import render_template, redirect, flash, url_for, request
from flask_login import login_required, current_user
from flask_babel import _ # type: ignore
from . import equipos
from app import db
from app.models import Equipo, EstadoEnum
from .forms import NuevoEquipo, EditEquipoForm
# Al principio de app/equipo/routes.py remplaza las tres líneas de utilidades por esta sola:
from app.utils import guardar_imagen_estandarizada, evaluar_estado_equipo, ejecutar_replica_a_verificacion, limpiar_imagenes_huerfanas, acceso_requerido, usuario_debe_bloquear_maestro

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
@acceso_requerido(roles=["Administrador", "Agente_1", "Agente_2", "Agente_3"])
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
            
            # Capturamos los booleanos del formulario
            equipo.es_maestro = form.es_maestro.data
            equipo.es_verificacion = form.es_verificacion.data
            
            # --- INTERCEPTOR DE LOG PASIVO ---
            # Si en tu formulario añadiste el checkbox 'confirmar_log', estampa la marca de forma segura
            if hasattr(form, 'confirmar_log') and form.confirmar_log.data:
                nota_log = "[LOG VERIFICADO Y VALIDADO CON ÉXITO]"
                if equipo.observacion:
                    equipo.observacion = f"{equipo.observacion} - {nota_log}"
                else:
                    equipo.observacion = nota_log
            
            # --- BLINDAJE POSICIONAL DE 8 IMÁGENES ---
            lista_imagenes = []
            for i in range(8):
                campo_imagen = form.imagenes[i] if i < len(form.imagenes.entries) else None
                if campo_imagen and campo_imagen.data and hasattr(campo_imagen.data, 'filename') and campo_imagen.data.filename != '':
                    nombre_foto = guardar_imagen_estandarizada(campo_imagen.data, subfolder='equipos')
                    lista_imagenes.append(nombre_foto)
                else:
                    lista_imagenes.append(None)
            equipo.imagenes = lista_imagenes

            # --- MÁQUINA DE ESTADOS PASIVA (EVALUADOR) ---
            # Evaluamos pasivamente el estado según el diagrama (Retorna tupla: Enum, Mensaje)
            nuevo_estado, mensaje_flujo = evaluar_estado_equipo(equipo)
            
            # Sincronizamos pasándole únicamente el Enum limpio
            equipo.estado = nuevo_estado
            equipo.actualizar_estado()  

            # --- DISPARADOR DE RÉPLICA CONTROLADO POR ESTADO ---
            if equipo.es_verificacion and equipo.estado not in [EstadoEnum.PENDIENTE_HASH, EstadoEnum.PENDIENTE_LOG] and not equipo.replica_ejecutada:
                ejecutar_replica_a_verificacion(equipo)

            # Persistencia de datos libre de excepciones de negocio
            db.session.add(equipo)
            db.session.commit()
            
            # Alertas visuales informativas según el hito del diagrama alcanzado
            if equipo.estado in [EstadoEnum.PENDIENTE_HASH, EstadoEnum.PENDIENTE_LOG]:
                flash(_(mensaje_flujo), "warning")  # Amarillo: Guardado exitoso pero faltan datos
            elif equipo.estado == EstadoEnum.FINALIZADO:
                flash(_(mensaje_flujo), "success")  # Verde: Flujo completado de inicio a fin
            else:
                flash(_(mensaje_flujo), "info")     # Azul: Registro inicializado o pendiente de fase 2
                
            rol_actual = current_user.rol.value

            if rol_actual == "Administrador":
                dest = 'equipo.lista_equipos'
            elif rol_actual == "Agente_3":
                dest = 'equipo.lista_equipos_auditor'  # <-- Redirección correcta para el Agente 3
            else:
                dest = 'equipo.lista_equipos_agente'   # Opciones para Agente_1 y Agente_2
                
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
@acceso_requerido(roles=["Administrador", "Agente_1", "Agente_2", "Agente_3"])
@login_required
def editar(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)
    form = EditEquipoForm(obj=equipo)
    
    # 1. Conservar estados de checkboxes en GET
    if request.method == 'GET':
        nota_log = "[LOG VERIFICADO Y VALIDADO CON ÉXITO]"
        if equipo.observacion and nota_log in equipo.observacion:
            form.confirmar_log.data = True
        else:
            form.confirmar_log.data = False
            
    # 2. Determinar si se bloquea por Regla de Equipo Maestro
    bloquear_campos = usuario_debe_bloquear_maestro(current_user, equipo)

    # 3. SOLUCIÓN PREGUNTA 1: Bloqueo masivo automático para el HTML
    campos_a_bloquear = [
        'es_maestro', 'es_verificacion', 'direccion', 'comision', 'cod_comision',
        'capacidad', 'municipio', 'departamento', 'equipo_marca', 'equipo_modelo',
        'equipo_serial', 'dd_marca', 'dd_modelo', 'dd_serial', 'sha_1', 'md5', 'proceso'
    ]
    if bloquear_campos:
        for nombre_campo in campos_a_bloquear:
            if nombre_campo in form:
                form[nombre_campo].render_kw = {'readonly': True, 'class': 'form-control bg-light'}

    while len(form.imagenes.entries) < form.imagenes.max_entries:
        form.imagenes.append_entry()

    if form.validate_on_submit():
        try:
            # Guardamos los valores originales de respaldo ANTES de poblar el objeto
            respaldo_serial = equipo.equipo_serial
            respaldo_maestro = equipo.es_maestro
            respaldo_verificacion = equipo.es_verificacion
            
            estado_anterior = equipo.estado.value if hasattr(equipo.estado, 'value') else equipo.estado
            
            # Poblamos el objeto con lo que viene de la web
            form.populate_obj(equipo)
            
            # 4. SOLUCIÓN CRÍTICA BACKEND: Si está bloqueado, forzamos los valores originales de la BD
            if bloquear_campos:
                equipo.es_maestro = respaldo_maestro
                equipo.es_verificacion = respaldo_verificacion
            else:
                # Si es administrador y los modificó en el form, aseguramos la persistencia
                equipo.es_maestro = form.es_maestro.data
                equipo.es_verificacion = form.es_verificacion.data

            # --- INTERCEPTOR DE LOG PASIVO EN EDICIÓN ---
            if hasattr(form, 'confirmar_log') and form.confirmar_log.data:
                nota_log = "[LOG VERIFICADO Y VALIDADO CON ÉXITO]"
                if not equipo.observacion or nota_log not in equipo.observacion:
                    equipo.observacion = f"{equipo.observacion or ''} {nota_log}".strip()

            # --- RECONSTRUCCIÓN POSICIONAL DE LAS IMÁGENES ---
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
                        
                    nombre_nuevo = guardar_imagen_estandarizada(campo_imagen.data, subfolder='equipos')
                    nuevas_imagenes.append(nombre_nuevo)
                else:
                    nuevas_imagenes.append(foto_antigua)
            
            equipo.imagenes = nuevas_imagenes

            # --- MÁQUINA DE ESTADOS PASIVA (EVALUADOR) ---
            nuevo_estado, mensaje_flujo = evaluar_estado_equipo(equipo)
            equipo.estado = nuevo_estado
            equipo.actualizar_estado()  

            # --- DISPARADOR DE RÉPLICA CONTROLADO POR ESTADO ---
            if equipo.es_verificacion and equipo.estado not in [EstadoEnum.PENDIENTE_HASH, EstadoEnum.PENDIENTE_LOG] and not equipo.replica_ejecutada:
                ejecutar_replica_a_verificacion(equipo)

            db.session.commit()
            
            if equipo.estado in [EstadoEnum.PENDIENTE_HASH, EstadoEnum.PENDIENTE_LOG]:
                flash(_(mensaje_flujo), "warning")
            elif equipo.estado == EstadoEnum.FINALIZADO:
                flash(_(mensaje_flujo), "success")
            else:
                flash(_(mensaje_flujo), "info")

            rol_actual = current_user.rol.value
            if rol_actual == "Administrador":
                dest = 'equipo.lista_equipos'
            elif rol_actual == "Agente_3":
                dest = 'equipo.lista_equipos_auditor'
            else:
                dest = 'equipo.lista_equipos_agente'
                
            return redirect(url_for(dest))

        except Exception as e:
            db.session.rollback()
            flash(f"Error de consistencia: {e}", "error")
            return redirect(url_for('equipo.editar', equipo_id=equipo_id))
        
    return render_template('equipo/editar.html', form=form, equipo=equipo, labels=labels, bloquear_campos=bloquear_campos)


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
            # 1. Leemos el archivo
            contenido = archivo.stream.read().decode("UTF-8-sig")
            stream = io.StringIO(contenido, newline=None)
            
            # 2. Adivinamos el delimitador (Tabulador, Punto y coma, o Coma)
            primera_linea = contenido.split('\n')[0]
            if '\t' in primera_linea:
                delimitador = '\t'
            elif ';' in primera_linea:
                delimitador = ';'
            else:
                delimitador = ','
            
            csv_input = csv.DictReader(stream, delimiter=delimitador)
            
            # 3. Normalizamos los encabezados (todo a minúsculas y sin espacios)
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
                
                # --- EXTRACCIÓN DE NUEVOS CAMPOS ---
                # Campos de texto normales
                tipo_disco_csv = fila.get('tipo_disco', '').strip()
                comision_csv = fila.get('comision', '').strip()
                municipio_csv = fila.get('municipio', '').strip()
                departamento_csv = fila.get('departamento', '').strip()
                
                # Campos Booleanos (Verdadero/Falso)
                # Si en el Excel ponen "1", "si" o "true", lo convertimos a True para MySQL
                str_maestro = fila.get('es_maestro', '0').strip().lower()
                es_maestro_bool = True if str_maestro in ['1', 'true', 'si', 's'] else False
                
                str_verificacion = fila.get('es_verificacion', '0').strip().lower()
                es_verificacion_bool = True if str_verificacion in ['1', 'true', 'si', 's'] else False

                # Instanciamos el modelo con TODOS los campos mapeados
                nuevo_equipo = Equipo(
                    nombre=nombre_csv,
                    equipo_serial=serial_csv,
                    equipo_marca=marca_csv,
                    equipo_modelo=modelo_csv,
                    
                    # Agregamos los nuevos campos aquí:
                    # (Asegúrate de que la parte izquierda coincida con tu modelo de base de datos)
                    dd_modelo=tipo_disco_csv, # O el campo donde guardes el tipo de disco
                    comision=comision_csv,
                    municipio=municipio_csv,
                    departamento=departamento_csv,
                    es_maestro=es_maestro_bool,
                    es_verificacion=es_verificacion_bool,
                    
                    usuario_id=current_user.id
                )
                
                # Evaluamos el estado inicial
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