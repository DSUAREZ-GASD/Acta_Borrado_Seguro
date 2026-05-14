import os
import uuid
from PIL import Image as PILImage, ImageOps
from flask import current_app
from app import db

# Definimos la constante fuera para que sea fácil de ajustar
STANDARD_SIZE = (1280, 720)

def guardar_imagen_estandarizada(file_storage, upload_folder=None):
    """Procesa y guarda una imagen en formato JPG estandarizado."""
    if not (file_storage and hasattr(file_storage, 'filename') and file_storage.filename):
        return None
    
    # Si no se pasa ruta, usamos la configuración de Flask por defecto
    if upload_folder is None:
        upload_folder = os.path.join(current_app.root_path, 'static', 'img')

    temp_filename = f"{uuid.uuid4()}.jpg" 
    file_path = os.path.join(upload_folder, temp_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        img = PILImage.open(file_storage)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        img = ImageOps.exif_transpose(img)
        img_estandarizada = ImageOps.contain(img, STANDARD_SIZE, PILImage.Resampling.LANCZOS)
        img_estandarizada.save(file_path, quality=85, optimize=True) # Calidad 85 es balance ideal
        
        return temp_filename
    except Exception as e:
        current_app.logger.error(f"Error procesando imagen: {e}")
        return None

def limpiar_imagenes_huerfanas():
    """Mantenimiento: Elimina archivos en disco que no están referenciados en la DB."""
    # Importamos los modelos aquí para evitar importación circular
    from app.models import Equipo, Actividad_verificacion
    
    img_d_ruta = os.path.join(current_app.root_path, 'static', 'img')
    
    # Consolidar imágenes de todas las tablas
    imagenes_validas_set = set()
    
    # Consultas optimizadas usando with_entities
    for registro in Equipo.query.with_entities(Equipo.imagenes).all():
        if registro[0]: imagenes_validas_set.update(registro[0])
            
    for registro in Actividad_verificacion.query.with_entities(Actividad_verificacion.evidencias).all():
        if registro[0]: imagenes_validas_set.update(registro[0])
            
    if not os.path.exists(img_d_ruta):
        return

    for img in os.listdir(img_d_ruta):
        if img not in imagenes_validas_set:
            try:
                os.remove(os.path.join(img_d_ruta, img))
            except Exception as e:
                current_app.logger.warning(f"No se pudo eliminar {img}: {e}")