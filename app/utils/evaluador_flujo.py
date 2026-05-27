from app.models import EstadoEnum

def evaluar_estado_equipo(equipo):
    """
    Recorre secuencialmente el diagrama de flujo de estados de arriba hacia abajo.
    Asigna el estado correspondiente sin bloquear la persistencia física en BD.
    
    Retorna:
        tuple: (EstadoEnum, str (mensaje_de_estado_o_alerta))
    """
    # Conteo real y posicional de evidencias (excluyendo vacíos)
    lista_imagenes = equipo.imagenes if equipo.imagenes else []
    cantidad_reales = sum(1 for img in lista_imagenes if img is not None and img != "")

    # -------------------------------------------------------------------------
    # COMPUERTA 1: ¿Equipo es Maestro?
    # -------------------------------------------------------------------------
    if equipo.es_maestro:
        # [Rama Izquierda] -> Bloquear imágenes inicio/fin (controlado en HTML) -> Gestión Admin
        return EstadoEnum.GESTION_ADMINISTRADOR, "Equipo Maestro: Queda bajo gestión exclusiva de Administrador."

    # -------------------------------------------------------------------------
    # COMPUERTA 2: ¿Equipo de verificación = SÍ?
    # -------------------------------------------------------------------------
    # Nota: La lógica de bifurcación de réplicas y mensajes informativos se evalúa aquí
    # pero no frena la transición de los estados lógicos siguientes.
    
    # -------------------------------------------------------------------------
    # COMPUERTA 3: ¿Hash validado? (SHA-1 o MD5 presentes)
    # -------------------------------------------------------------------------
    tiene_hash = (equipo.sha_1 and equipo.sha_1.strip() != "") or (equipo.md5 and equipo.md5.strip() != "")
    
    if not tiene_hash:
        # [Flecha NO] -> Mostrar error hash -> Regresar a formulario (Estado pasivo de espera)
        return EstadoEnum.PENDIENTE_HASH, "Equipo guardado. Estado: PENDIENTE HASH. Se requiere SHA-1 o MD5 para avanzar en el flujo."

    # -------------------------------------------------------------------------
    # COMPUERTA 4: ¿Tiene log correcto? (Validación en Observaciones)
    # -------------------------------------------------------------------------
    tiene_log = equipo.observacion and any(palabra in equipo.observacion.lower() for palabra in ["log", "reporte", "verificado"])
    
    if not tiene_log and cantidad_reales > 0:
        # [Flecha NO] -> Mostrar Error: Log obligatorio -> Regresar a formulario
        return EstadoEnum.PENDIENTE_LOG, "Equipo guardado. Estado: PENDIENTE LOG. Debe registrar la confirmación en las observaciones."

    # -------------------------------------------------------------------------
    # COMPUERTA 5: ¿Fase 2 completada? (Caja equipo + fin copia) & Evaluación de Cantidad
    # -------------------------------------------------------------------------
    # Si tiene Hash y tiene Log, evaluamos las evidencias físicas (Estándar de 8 fotos)
    if cantidad_reales == 0:
        return EstadoEnum.REGISTRADO, "Equipo inicializado con éxito. Listo para la carga de evidencias."
    
    elif cantidad_reales < 8:
        # [Flecha NO] -> Tiene que tener todas las imágenes para generar PDF
        return EstadoEnum.PENDIENTE_FASE_2, f"Evidencias en proceso: Fase 2 incompleta ({cantidad_reales}/8 imágenes cargadas)."
    
    elif cantidad_reales == 8:
        # [Camino Verde] -> Cantidad de imágenes completa -> Habilitar Generar PDF
        return EstadoEnum.FINALIZADO, "Flujo completado con éxito. Cantidad de imágenes completa. Listo para generar certificación PDF."

    return EstadoEnum.REGISTRADO, ""

def evaluar_estado_verificacion(actividad):
    """
    Evalúa secuencialmente el flujo del diagrama para las Actas de Verificación.
    """
    lista_evidencias = actividad.evidencias if actividad.evidencias else []
    cantidad_reales = sum(1 for img in lista_evidencias if img is not None and img != "")

    # 1. COMPUERTA HASH (SHA-1 o MD5)
    tiene_hash = (actividad.sha_1 and actividad.sha_1.strip() != "") or (actividad.md5 and actividad.md5.strip() != "")
    if not tiene_hash and cantidad_reales > 0:
        return EstadoEnum.PENDIENTE_HASH, "Acta guardada. Estado: PENDIENTE HASH. Se requiere SHA-1 o MD5 para continuar."

    # 2. COMPUERTA LOG CORREGIDA: Buscamos la etiqueta en el campo 'observacion'
    # Validamos si existe el texto de control exacto que inyectan las rutas
    tiene_log = actividad.observacion and "[LOG VERIFICADO Y VALIDADO CON ÉXITO]" in actividad.observacion
    
    if not tiene_log and cantidad_reales > 0:
        return EstadoEnum.PENDIENTE_LOG, "Acta guardada. Estado: PENDIENTE LOG. Marque el checkbox de validación de registros log."

    # 3. COMPUERTA CANTIDADES
    if cantidad_reales == 0:
        return EstadoEnum.REGISTRADO, "Acta de verificación inicializada. Lista para carga de evidencias."
    elif cantidad_reales < 5:
        return EstadoEnum.PENDIENTE_FASE_2, f"Evidencias de verificación en proceso ({cantidad_reales}/5 cargadas)."
    elif cantidad_reales == 5:
        return EstadoEnum.FINALIZADO, "Verificación completada con éxito. Listo para emisión de acta firmada."

    return EstadoEnum.REGISTRADO, ""