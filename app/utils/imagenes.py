import os
import uuid
from PIL import Image as PILImage, ImageOps
from flask import current_app
from app import db

# Constante de tamaño estandarizado
STANDARD_SIZE = (1280, 720)

def guardar_imagen_estandarizada(file_storage, subfolder=''):
    """
    Procesa y guarda una imagen en formato JPG estandarizado.
    
    :param file_storage: El archivo proveniente del formulario (request.files).
    :param subfolder: Subcarpeta dentro de static/uploads/ (ej: 'equipos' o 'verificaciones').
    """
    if not (file_storage and hasattr(file_storage, 'filename') and file_storage.filename):
        return None
    
    # Construimos la ruta dinámica basada en la subcarpeta deseada
    # Resultado esperado: /tu_proyecto/app/static/uploads/equipos (o verificaciones)
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', subfolder)

    temp_filename = f"{uuid.uuid4()}.jpg" 
    file_path = os.path.join(upload_folder, temp_filename)
    
    # Crea la estructura completa de carpetas si no existe
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        img = PILImage.open(file_storage)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        img = ImageOps.exif_transpose(img)
        img_estandarizada = ImageOps.contain(img, STANDARD_SIZE, PILImage.Resampling.LANCZOS)
        
        # Calidad 85 es el balance ideal entre peso y nitidez
        img_estandarizada.save(file_path, 'JPEG', quality=85, optimize=True) 
        
        return temp_filename
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
    subcarpetas = ['equipos', 'verificaciones']
    base_uploads_path = os.path.join(current_app.root_path, 'static', 'uploads')

    for subfolder in subcarpetas:
        target_dir = os.path.join(base_uploads_path, subfolder)
        
        if not os.path.exists(target_dir):
            continue

        # Escaneamos cada subcarpeta de forma independiente
        for img in os.listdir(target_dir):
            if img not in imagenes_validas_set:
                try:
                    os.remove(os.path.join(target_dir, img))
                    current_app.logger.info(f"Imagen huérfana eliminada: {subfolder}/{img}")
                except Exception as e:
                    current_app.logger.warning(f"No se pudo eliminar {subfolder}/{img}: {e}")