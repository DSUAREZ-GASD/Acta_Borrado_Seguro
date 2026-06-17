from app.models import EstadoEnum

def evaluar_estado_equipo(equipo):
    """
    Mantiene su lógica secuencial para la tabla de equipos físicos (8 imágenes).
    """
    lista_imagenes = equipo.imagenes if equipo.imagenes else []
    cantidad_reales = sum(1 for img in lista_imagenes if img is not None and img != "")

    if equipo.es_maestro:
        return EstadoEnum.GESTION_ADMINISTRADOR, "Equipo Maestro: Queda bajo gestión exclusiva de Administrador."

    tiene_hash = (equipo.sha_1 and equipo.sha_1.strip() != "") or (equipo.md5 and equipo.md5.strip() != "")
    if not tiene_hash:
        return EstadoEnum.PENDIENTE_HASH, "Equipo guardado. Estado: PENDIENTE HASH. Se requiere SHA-1 o MD5 para avanzar."

    nota_log = "[LOG VERIFICADO Y VALIDADO CON ÉXITO]"
    tiene_log = equipo.observacion and nota_log in equipo.observacion
    if not tiene_log:
        return EstadoEnum.PENDIENTE_LOG, "Equipo guardado. Estado: PENDIENTE LOG. Debe registrar la confirmación del Log."

    if cantidad_reales == 0:
        return EstadoEnum.REGISTRADO, "Equipo inicializado con éxito. Listo para la carga de evidencias."
    elif cantidad_reales < 8:
        return EstadoEnum.PENDIENTE_FASE_2, f"Evidencias en proceso: Fase 2 incompleta ({cantidad_reales}/8 imágenes cargadas)."
    elif cantidad_reales == 8:
        return EstadoEnum.FINALIZADO, "Flujo completado con éxito. Listo para generar certificación PDF."

    return EstadoEnum.REGISTRADO, ""


def evaluar_estado_verificacion(actividad):
    """
    EVALUADOR AJUSTADO: Extrae el HASH y LOG del equipo vinculado (Relación 1-a-1).
    Usa el estándar definitivo de 7 imágenes para la verificación de carpetas de escrutinio.
    """
    lista_evidencias = actividad.evidencias if actividad.evidencias else []
    cantidad_reales = sum(1 for img in lista_evidencias if img is not None and str(img).strip() != "")

    # Si por alguna inconsistencia el equipo no está mapeado en memoria, frena preventivamente
    if not actividad.equipo:
        return EstadoEnum.REGISTRADO, "Acta sin equipo vinculado."

    # 1. COMPUERTA HASH: Extraída directamente desde la única fuente de verdad (el equipo)
    equipo_padre = actividad.equipo
    tiene_hash = (equipo_padre.sha_1 and equipo_padre.sha_1.strip() != "") or (equipo_padre.md5 and equipo_padre.md5.strip() != "")
    if not tiene_hash:
        return EstadoEnum.PENDIENTE_HASH, "Acta guardada. Estado: PENDIENTE HASH en el equipo. Se requiere SHA-1 o MD5."

    # 2. COMPUERTA LOG: Extraída desde las observaciones del equipo físico
    tiene_log = equipo_padre.observacion and "[LOG VERIFICADO Y VALIDADO CON ÉXITO]" in equipo_padre.observacion
    if not tiene_log:
        return EstadoEnum.PENDIENTE_LOG, "Acta guardada. Estado: PENDIENTE LOG en el equipo. Requiere validación de registros log."

    # 3. COMPUERTA CANTIDADES (Sincronizada a un máximo de 7 imágenes de actas)
    if cantidad_reales == 0:
        return EstadoEnum.REGISTRADO, "Acta de verificación inicializada. Lista para carga de evidencias."
    elif cantidad_reales < 7:
        return EstadoEnum.PENDIENTE_FASE_2, f"Evidencias de verificación en proceso ({cantidad_reales}/7 cargadas)."
    elif cantidad_reales == 7:
        return EstadoEnum.FINALIZADO, "Verificación completada con éxito. Listo para emisión de acta firmada."

    return EstadoEnum.REGISTRADO, ""