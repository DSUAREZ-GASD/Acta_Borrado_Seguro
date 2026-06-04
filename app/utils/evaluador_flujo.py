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
        return EstadoEnum.GESTION_ADMINISTRADOR, "Equipo Maestro: Queda bajo gestión exclusiva de Administrador."

    # -------------------------------------------------------------------------
    # COMPUERTA 2: ¿Tiene Hash validado? (SHA-1 o MD5 estrictos)
    # -------------------------------------------------------------------------
    tiene_hash = (equipo.sha_1 and equipo.sha_1.strip() != "") or (equipo.md5 and equipo.md5.strip() != "")
    
    # AJUSTE: Si no tiene Hash, se degrada a PENDIENTE_HASH sin importar cuántas fotos tenga
    if not tiene_hash:
        return EstadoEnum.PENDIENTE_HASH, "Equipo guardado. Estado: PENDIENTE HASH. Se requiere SHA-1 o MD5 para avanzar en el flujo."

    # -------------------------------------------------------------------------
    # COMPUERTA 3: ¿Tiene log verificado de forma estricta?
    # -------------------------------------------------------------------------
    # AJUSTE: Estandarizado para buscar la etiqueta exacta que inyecta la ruta de edición
    nota_log = "[LOG VERIFICADO Y VALIDADO CON ÉXITO]"
    tiene_log = equipo.observacion and nota_log in equipo.observacion
    
    # AJUSTE: Si tiene Hash pero le borraron el Log, cae aquí inmediatamente
    if not tiene_log:
        return EstadoEnum.PENDIENTE_LOG, "Equipo guardado. Estado: PENDIENTE LOG. Debe registrar la confirmación del Log en las observaciones."

    # -------------------------------------------------------------------------
    # COMPUERTA 4: Evaluación de Evidencias Físicas (Fase 2)
    # -------------------------------------------------------------------------
    # Si llegó aquí, ya tiene GARANTIZADO el Hash y el Log. Evaluamos cantidades:
    if cantidad_reales == 0:
        return EstadoEnum.REGISTRADO, "Equipo inicializado con éxito. Listo para la carga de evidencias."
    
    elif cantidad_reales < 8:
        return EstadoEnum.PENDIENTE_FASE_2, f"Evidencias en proceso: Fase 2 incompleta ({cantidad_reales}/8 imágenes cargadas)."
    
    elif cantidad_reales == 8:
        return EstadoEnum.FINALIZADO, "Flujo completado con éxito. Cantidad de imágenes completa. Listo para generar certificación PDF."

    return EstadoEnum.REGISTRADO, ""


def evaluar_estado_verificacion(actividad):
    """
    Evalúa secuencialmente el flujo del diagrama para las Actas de Verificación.
    """
    lista_evidencias = actividad.evidencias if actividad.evidencias else []
    cantidad_reales = sum(1 for img in lista_evidencias if img is not None and img != "")

    # 1. COMPUERTA HASH (Eliminamos la restricción de 'cantidad_reales > 0')
    # AJUSTE: Si borran el hash, cae de inmediato independientemente de las fotos cargadas
    tiene_hash = (actividad.sha_1 and actividad.sha_1.strip() != "") or (actividad.md5 and actividad.md5.strip() != "")
    if not tiene_hash:
        return EstadoEnum.PENDIENTE_HASH, "Acta guardada. Estado: PENDIENTE HASH. Se requiere SHA-1 o MD5 para continuar."

    # 2. COMPUERTA LOG (Eliminamos la restricción de 'cantidad_reales > 0')
    # AJUSTE: Si tiene hash pero le quitan el log, frena aquí
    tiene_log = actividad.observacion and "[LOG VERIFICADO Y VALIDADO CON ÉXITO]" in actividad.observacion
    if not tiene_log:
        return EstadoEnum.PENDIENTE_LOG, "Acta guardada. Estado: PENDIENTE LOG. Marque el checkbox de validación de registros log."

    # 3. COMPUERTA CANTIDADES (Solo se evalúa si las dos compuertas de arriba están aprobadas)
    if cantidad_reales == 0:
        return EstadoEnum.REGISTRADO, "Acta de verificación inicializada. Lista para carga de evidencias."
    elif cantidad_reales < 5:
        return EstadoEnum.PENDIENTE_FASE_2, f"Evidencias de verificación en proceso ({cantidad_reales}/5 cargadas)."
    elif cantidad_reales == 5:
        return EstadoEnum.FINALIZADO, "Verificación completada con éxito. Listo para emisión de acta firmada."

    return EstadoEnum.REGISTRADO, ""