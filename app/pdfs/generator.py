from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import  colors
from flask import current_app # Ruta base de tu aplicación
from reportlab.lib.utils import ImageReader # Libreria para agregar imagenes
from reportlab.lib.units import inch

import os

def generar_pdf(nombre_archivo, firma, equipo):        
    # Establecer la ruta del archivo PDF
    ruta_pdf = os.path.join(current_app.root_path, 'static', 'tmp', nombre_archivo)
    
    # Crear la carpeta si no existe
    if not os.path.exists(os.path.dirname(ruta_pdf)):
        os.makedirs(os.path.dirname(ruta_pdf))  
        
    # Creamos un objeto Canvas para el PDF
    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    width, height = letter
    
    # Configuración de la fuente
    c.setFont("Helvetica-Bold", 16)
    
    # Información del equipo
    c.drawString(100, height - 100, f"Equipo: {equipo.nombre}")
    c.drawString(100, height - 130, f"Comisión: {equipo.comision}")
    
    # Configuración tabla de firmas
    position_x = 100
    position_y = height - 180
    row_height = 45  # Aumenta el espacio entre filas
    col_width = 160
    row_height_head = 5
    img_firma_width, img_firma_heigth = 80, 40

    # Enunciados de la primera columna
    enunciados = ["Rep. Registraduría:", "Rep. Auditoría externa:", "Rep. Procuraduría:", "Rep. Procuraduría:", "Rep. Contratista:"]
    nombres_responsables = [firma.name1, firma.name2, firma.name3, firma.name4, firma.name5]

    # Encabezado de tabla
    c.setFont("Helvetica-Bold", 12)
    c.drawString(position_x, position_y + row_height_head, "Entidad Responsable")
    c.drawString(position_x + col_width, position_y + row_height_head, "Nombre responsable")
    c.drawString(position_x + 2 * col_width, position_y + row_height_head, "Firma")

    # Dibujar filas de la tabla
    c.setFont("Helvetica-Bold", 10)
    for i, enunciado in enumerate(enunciados):
        
        # Verificar si la posición y está cerca del borde inferior
        if position_y - (i + 1) * row_height < 50:
            c.showPage()  # Nueva página
            # Redefinir posición en la nueva página
            position_y = height - 180
            c.setFont("Helvetica-Bold", 12)
            c.drawString(position_x, position_y + row_height, "Entidad Responsable")
            c.drawString(position_x + col_width, position_y + row_height, "Nombre responsable")
            c.drawString(position_x + 2 * col_width, position_y + row_height, "Firma")
            c.setFont("Helvetica-Bold", 10)

        # Enunciados de la primera columna
        c.drawString(position_x, position_y - (i + 1) * row_height, enunciado)
        
        # Segunda columna
        c.drawString(position_x + col_width, position_y - (i + 1) * row_height, nombres_responsables[i])

        # Tercera columna
        if i < len(firma.firmas) and firma.firmas[i]:
            ruta_firma = os.path.join(current_app.root_path, 'firma', 'static', 'firmas', firma.firmas[i])
            if os.path.exists(ruta_firma):
                img_firma = ImageReader(ruta_firma)
                # Ajustar la posición de la firma para evitar superposición
                center_position = position_y - (i + 1) * row_height - img_firma_heigth / 2  # Centrado en la celda
                c.drawImage(img_firma, position_x + 2 * col_width, center_position, width=img_firma_width, height=img_firma_heigth)
            else:
                c.drawString(position_x + 2 * col_width, position_y - (i + 1) * row_height, "Firma no encontrada")
        else:
            # Línea vacía para firmas no encontradas o sin firma
            c.line(position_x + 2 * col_width, position_y - (i + 1) * row_height - 5,
                position_x + 2 * col_width + 100, position_y - (i + 1) * row_height - 5)

    # Configuración de la tabla de imágenes
    x_offset = 100    # Posición horizontal de inicio
    y_offset = position_y - len(enunciados) * row_height - 180  # Posición vertical de inicio (espacio para el nombre y precio)
    img_width, img_height = 150, 150  # Tamaño de cada imagen
    cols = 2  # Número de columnas
    padding = 10  # Espacio entre imágenes
    max_rows = 2 # Maximo numero de fila
    
    # Contador de filas
    current_row = 0
    
    # Iterar sobre las imágenes y dibujarlas en una cuadrícula
    for i, img_name in enumerate(equipo.imagenes[:8]):  # Limitar a 8 imágenes
        # Calcular la posición x e y para cada imagen
        col = i % cols
        row = i // cols
        x = x_offset + col * (img_width + padding)
        y = y_offset - (row %  max_rows) * (img_height + padding)

        # Ruta de la imagen actual
        ruta_imagen = os.path.join(current_app.root_path, 'static', 'imagenes', img_name)
        
        # Verificar si la imagen existe antes de dibujarla
        if os.path.exists(ruta_imagen):
            img = ImageReader(ruta_imagen)
            c.drawImage(img, x, y, width=img_width, height=img_height)
        else:
            c.drawString(x, y + (img_height / 2), "Imagen no encontrada")
            
        # Incrementar el contador de filas y verificar si se requiere una nueva página
        if (i + 1) %  (cols * max_rows) == 0 and i + 1 < len(equipo.imagenes):
            c.showPage()
            
    c.save()
    return ruta_pdf





