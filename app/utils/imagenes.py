import os
import uuid
import unicodedata
import re
from PIL import Image as PILImage, ImageOps
from flask import current_app

# Constante de tamaño estandarizado
STANDARD_SIZE = (1280, 720)

# Mapeo de slots a nombres canónicos (sin extensión)
SLOT_FILENAMES = {
    0: 'foto_caja_equipo',
    1: 'foto_equipo',
    2: 'foto_serial_equipo',
    3: 'foto_identificacion_comision',
    4: 'foto_inicio_generacion',
    5: 'foto_fin_generacion',
    6: 'foto_inicio_borrado',
    7: 'foto_fin_borrado',
}


def _sanitize_component(value: str, max_length: int = 100) -> str:
    """Normaliza una cadena para usar en nombres de carpeta.

    - Quita tildes y caracteres Unicode no ASCII.
    - Reemplaza espacios por guiones bajos.
    - Elimina caracteres no alfanuméricos excepto guión bajo y guión medio.
    - Convierte a mayúsculas.
    """
    if not value:
        return 'UNKNOWN'
    # Normalizar Unicode
    value = unicodedata.normalize('NFKD', str(value))
    value = value.encode('ascii', 'ignore').decode('ascii')
    # Reemplazar espacios y múltiples separadores por un guion bajo
    value = re.sub(r'[\s]+', '_', value.strip())
    # Eliminar caracteres indeseados
    value = re.sub(r'[^A-Za-z0-9_\-]', '', value)
    value = value.upper()
    return value[:max_length]


def guardar_imagen_estandarizada(file_storage, subfolder='', meta: dict | None = None, slot: int | None = None):
    """
    Procesa y guarda una imagen en formato JPG estandarizado usando la
    jerarquía: subfolder/departamento/municipio/comision/equipo/archivo.jpg

    :param file_storage: El archivo proveniente del formulario (request.files).
    :param subfolder: Subcarpeta dentro de static/uploads/ (ej: 'equipos' o 'verificaciones').
    :param meta: Diccionario opcional con keys 'departamento','municipio','comision','equipo'
    :param slot: Índice del slot (0..7) para nombrar el archivo según convención.
    :return: Ruta relativa dentro de la subcarpeta (por ejemplo
             'ANTIOQUIA/MEDELLIN/COMISION_001/ILE3-001/foto_serial_equipo.jpg')
    """
    if not (file_storage and hasattr(file_storage, 'filename') and file_storage.filename):
        return None

    upload_base = os.path.join(current_app.root_path, 'static', 'uploads')
    upload_folder = os.path.join(upload_base, subfolder)

    # Determinar componentes desde meta con fallbacks
    meta = meta or {}
    departamento = _sanitize_component(meta.get('departamento') or meta.get('departamento_raw'))
    municipio = _sanitize_component(meta.get('municipio') or meta.get('municipio_raw'))
    # Preferir código de comisión si existe, si no usar el nombre
    comision_raw = meta.get('cod_comision') or meta.get('comision') or meta.get('cod_comision_raw')
    comision = _sanitize_component(str(comision_raw))
    equipo_name = _sanitize_component(meta.get('equipo') or meta.get('equipo_raw') or meta.get('nombre'))

    # Construir ruta destino
    dest_dir = os.path.join(upload_folder, departamento, municipio, comision, equipo_name)
    os.makedirs(dest_dir, exist_ok=True)

    # Determinar nombre de archivo según slot
    ext = '.jpg'
    if slot is not None and slot in SLOT_FILENAMES:
        filename = f"{SLOT_FILENAMES[slot]}{ext}"
    else:
        # Comportamiento retrocompatible: UUID
        filename = f"{uuid.uuid4()}{ext}"

    dest_path = os.path.join(dest_dir, filename)

    try:
        img = PILImage.open(file_storage)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        img = ImageOps.exif_transpose(img)
        img_estandarizada = ImageOps.contain(img, STANDARD_SIZE, PILImage.Resampling.LANCZOS)

        # Guardar en un archivo temporal y reemplazar atómicamente
        tmp_path = f"{dest_path}.{uuid.uuid4()}.tmp"
        img_estandarizada.save(tmp_path, 'JPEG', quality=85, optimize=True)
        os.replace(tmp_path, dest_path)

        # Retornar la ruta relativa POSIX dentro de la subcarpeta
        rel_path = os.path.relpath(dest_path, upload_folder)
        return rel_path.replace(os.path.sep, '/')
    except Exception as e:
        current_app.logger.error(f"Error procesando imagen en {subfolder}: {e}")
        return None

def limpiar_imagenes_huerfanas():
    """Mantenimiento: Elimina archivos en disco que no están referenciados en la DB."""
    # Importamos los modelos aquí para evitar importación circular
    from app.models import Equipo, Actividad_verificacion
    
    # Consolidar imágenes válidas desde la base de datos
    imagenes_validas_set = set()
    
    # Consultas optimizadas usando with_entities
    for registro in Equipo.query.with_entities(Equipo.imagenes).all():
        if registro[0]: 
            imagenes_validas_set.update(registro[0])
            
    for registro in Actividad_verificacion.query.with_entities(Actividad_verificacion.evidencias).all():
        if registro[0]: 
            imagenes_validas_set.update(registro[0])
            
    # Mapeamos las subcarpetas que queremos auditar
    subcarpetas = ['equipos', 'verificaciones', 'firmas']
    base_uploads_path = os.path.join(current_app.root_path, 'static', 'uploads')

    for subfolder in subcarpetas:
        target_dir = os.path.join(base_uploads_path, subfolder)

        if not os.path.exists(target_dir):
            continue

        # Recorrer recursivamente todos los archivos dentro de la subcarpeta
        for root, _dirs, files in os.walk(target_dir):
            for f in files:
                # Construir ruta relativa POSIX con respecto a la subcarpeta
                abs_path = os.path.join(root, f)
                rel_path = os.path.relpath(abs_path, target_dir).replace(os.path.sep, '/')
                if rel_path not in imagenes_validas_set:
                    try:
                        os.remove(abs_path)
                        current_app.logger.info(f"Imagen huérfana eliminada: {subfolder}/{rel_path}")
                    except Exception as e:
                        current_app.logger.warning(f"No se pudo eliminar {subfolder}/{rel_path}: {e}")