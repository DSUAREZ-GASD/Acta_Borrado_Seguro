from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import  colors
from flask import current_app # Ruta base de tu aplicación
from reportlab.lib.utils import ImageReader # Libreria para agregar imagenes
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.units import cm
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

def generar_pdf(nombre_archivo, equipo):        
    ruta_pdf = os.path.join(current_app.root_path, 'static', 'tmp', nombre_archivo)
    
    # Inicializa la lista de filas para la tabla
    filas_imagenes = []
    y,x = 10, 10
    
    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    # Limitar a 8 imágenes y preparar filas para la tabla
    for i in range(min(len(equipo.imagenes), 8)):
        img_name = equipo.imagenes[i]
        ruta_imagen = os.path.join(current_app.root_path, 'static', 'img', img_name)
        # Verificar si la imagen existe
        if os.path.exists(ruta_imagen):
            try:
                img = ImageReader(ruta_imagen)
                # Agregar la imagen a la tabla
                c.drawImage(img, x, y, width=1*inch, height=1*inch)
                filas_imagenes.append([img, "", img_name])  # Coloca la imagen, espacio vacío y el nombre de la imagen
                y += 1.5 * inch
            except Exception as e:
                print(f"Error al agregar imagen {img_name}: {e}")
                filas_imagenes.append(["Error al cargar la imagen", "", img_name])
        else:
            filas_imagenes.append(["Imagen no encontrada", "", img_name])
    
    c.save()
    
    # Crear la carpeta si no existe
    if not os.path.exists(os.path.dirname(ruta_pdf)):
        os.makedirs(os.path.dirname(ruta_pdf))  
    
    # Insertar los datos de los representantes en las filas de firmas
    
    # Configuración del PDF
    pdf = SimpleDocTemplate(
        ruta_pdf, pagesize=letter,
        leftMargin=1*cm,  # Margen izquierdo de 1 cm
        rightMargin=1*cm,  # Margen derecho de 1 cm
        topMargin=1*cm,  # Margen superior de 1 cm
        bottomMargin=1*cm  # Margen inferior de 1 cm
    )
    
    elementos = []
    
    # Estilos personalizados para párrafos
    estilos = getSampleStyleSheet()

    # Crear un estilo de párrafo con tamaño de letra personalizado
    estilos.add(ParagraphStyle(name="EstiloGrande", parent=estilos["Normal"], fontSize=9, leading=12,alignment=TA_CENTER))
    estilos.add(ParagraphStyle(name="EstiloMediano", parent=estilos["Normal"], fontSize=8, leading=12, alignment=TA_JUSTIFY))
    estilos.add(ParagraphStyle(name="EstiloPequeno", parent=estilos["Normal"], fontSize=7, leading=12, alignment=TA_CENTER))

    # Datos de la tabla con encabezados
    encabezados = ["IMG REGIS",Paragraph("<b>ACTA INDIVIDUAL PARA LA GENERACION DE LAS IMAGENES DE LA COPIA DE SEGURIDAD DE LOS DISCOS DUROS Y BORRADO SEGURO DE EQUIPOS DE ESCRUTINIO UTILIZADOS EN LAS CONSULTAS POPULARES PARA LA CONFORMACIÓN DEL ÁREA METROPOLITANA DEL SUROCCIDENTE DE COLOMBIA Y DEL PIEDEMONTE AMAZÓNICO Y ELECCIÓN DE LAS JUNTAS ADMINISTRADORAS LOCALES (JAL) 2024.</b>", estilos["EstiloPequeno"])]
    datos = [
        [],
        [Paragraph("<b>INTRODUCCIÓN</b>", estilos["EstiloGrande"])],
        [],
        [Paragraph("<b>DESCRIPCION:</b> Esta diligencia tiene como fin ejecutar el procedimiento descrito en el memorando GI-XXXX  del XX de noviembre de 2024 y el PROTOCOLO DE GENERACION DE COPIA DE SEGURIDAD DE LOS DISCOS DUROS Y BORRADO SEGURO DE LOS EQUIPOS DE COMPUTO UTILIZADOS EN LAS COMISIONES ESCRUTADORAS, aprobado por la supervisión del contrato, en cumplimiento al cronograma de actividades establecido para las Consultas Populares para la conformación del Área Metropolitana del Suroccidente de Colombia y del Piedemonte Amazónico y Elección de las Juntas Administradoras Locales (JAL) 2024 y lo estipulado en el Contrato No. 043 de 2024.",estilos["EstiloMediano"])],
        [],
        ["IDENTIFICACION DEL LUGAR DONDE SE ENCUENTRAN UBICADOS LOS EQUIPOS"],
        [""],
        ["Dirección:","Cra 10 # 17 – 72 Piso 3"],
        ["Ciudad:", "Bogotá D.C."],
        ["nombre del Edificio:","WTC I"],
        ["Fecha:", equipo.fecha_hora_inicio.strftime('%Y-%m-%d')],
        ["Hora:", equipo.fecha_hora_inicio.strftime('%H:%M:%S')],
        [],
        ["IDENTIFICACION DEL EQUIPO A EJECUTAR PROCEDIMIENTO"],
        ["Escrutinio/Comisión:", equipo.comision],
        ["Municipio:",equipo.municipio],
        ["Departamento:", equipo.departamento],
        ["EQUIPO", "", "", "DISCO DURO", ""],
        ["Marca:",equipo.equipo_marca,"","Marca:",equipo.dd_marca],
        ["Modelo:",equipo.equipo_modelo,"","Modelo:",equipo.dd_modelo],
        ["Serial:",equipo.equipo_serial,"","Capacidad:","XXXXX"],
        ["","","","Serial:",equipo.dd_serial],
        [],
        ["SOFTWARE PARA GENERAR IMAGEN DE LAS COPIAS DE SEGURIDAD"],
        [],
        ["Nombre del software:","FTK imager" ],
        ["Versión del software:","4.7.1.2" ],
        ["Tipo Licencia:", "FREE"],
        [],
        ["SOFTWARE PARA BORRADO SEGURO"],
        [],
        ["Nombre del software:","SHRED" ],
        ["Versión del software:","9.1" ],
        ["Tipo Licencia:", "GNU"],
        [],
        [],
        ["IDENTIFICACION DE LA IMAGEN DE LA COPIA DE SEGURIDAD"],
        ["La copia de seguridad del equipo tendrá las siguientes características:"],
        ["Nombre:", equipo.nombre ],
        ["HASH (SHA-1):", equipo.sha_1 ],
        ["La copia de seguridad será almacenada en un medio de almacenamiento con las siguientes características: Cada disco duro debe estar marcado con una etiqueta con esta misma información"],
        ["Marca:","SEAGATE" ],
        ["Capacidad:","18 TB" ],
        [""],
        ["Observación:", equipo.observacion],
        [],
        [],
        ["PROTOCOLO REALIZADO POR CADA EQUIPO" ],
        ["DESCRIPCION - SE REALIZARÁ ESTE PROCEDIMIENTO DE ACUERDO CON EL LINEAMIENTO ESTABLECIDO POR LA REGISTRADURIA NACIONAL DEL ESTADO CIVIL"],
        ["Identificado el equipo respectivo, al mismo se le insertará el medio de almacenamiento en el que se va a copiar imagem de la copia de seguridad"],
        ["Se procederá a realizar el proceso de obtención de la imagen de la copia de seguridad del disco duro del respectivo equipo de computo de escrutinio. Para lo anterior se ejecutará el programa correspondiente para la generación de la misma."],
        ["Terminado el proceso se copia la imagen de la copia de seguridad al disco duro arriba mencionado."],
        ["Se procederá a realizar el proceso de borrado seguro del disco duro del equipo de la comisión"],
        ["escrutadora. Para lo anterior se ejecutará el programa correspondiente para el borrado seguro.", ],
        ["Posteriormente, se tomarán las siguientes fotos del proceso: (Dichas fotos se anexaran a la presente acta.)"],
        [],
        [],
        ["1.    Foto de la caja del equipo " ],
        ["2.    Foto del equipo"],
        ["3.    Foto serial del equipo "],
        ["4.    Foto de la Identificación de la comisión"],
        ["5.    Foto inicio de generación de la imagen de la copia de seguridad "],
        ["6.    Foto finalización de la generación de la imagen de la copia de seguridad "],
        ["7.    Foto inicio del borrado ", ],
        ["8.    Foto finalización del borrado"],
        [],
        [],
        ["FIRMAS"],
        [f"Para constancia se firma en formato PDF con firma digita {equipo.fecha_hora_fin.strftime('%H:%M:%S')}  {equipo.fecha_hora_fin.strftime('%Y-%m-%d')} por quienes en ella intervienen"],
        ["Observaciones: Para dar claridad en la nitidez de las fotos se adjunta medio magnético al acta de cierre con la consolidación del registro fotográfico tomado por cada copia de seguridad"],
        [],
        [f"Rep. XXXXXXX", "Nombre: XXXXXXX", "Firma: XXXXXXX"],
        [f"Rep. XXXXXXX", "Nombre: XXXXXXX", "Firma: XXXXXXX"],
        [f"Rep. XXXXXXX", "Nombre: XXXXXXX", "Firma: XXXXXXX"],
        [f"Rep. XXXXXXX", "Nombre: XXXXXXX", "Firma: XXXXXXX"],
        [f"Rep. XXXXXXX", "Nombre: XXXXXXX", "Firma: XXXXXXX"],
        [],
        ["REGISTRO FOTOGRAFICO" ],
        [],
        [filas_imagenes[0][0] if len(filas_imagenes) > 0 else "Sin imagen", "", "", ""],
        ["1. Foto de la caja del equipo", "", "", "2. Foto del equipo"],
        [],
        [],
        ["3. Foto serial del equipo ", "", "", "4. Foto de la Identificación de la comisión"],
        [],
        [],
        ["5. Foto inicio de generación de la imagen de la copia de seguridad ", "", "", "6. Foto finalización de la generación de la imagen de la copia de seguridad"],
        [],
        [],
        ["7. Foto inicio del borrado", "", "", "8. Foto finalización del borrado"]       
    ]
    

    data_tabla = [encabezados] + datos  # Combinar encabezados y datos

    # Crear la tabla
    tabla = Table(data_tabla, colWidths = [132, 132, 24, 132, 132])

    # Aplicar estilos
    estilos = TableStyle([
        # Estilo general
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),  # Bordes
        ("SPAN", (1, 0), (4, 0)),  #titulo formato
        ("SPAN", (0, 2), (4, 2)),  #introduccion
        ("SPAN", (0, 3), (4, 3)),  
        ("SPAN", (0, 4), (4, 4)), 
        ("SPAN", (0, 5), (4, 5)),
        ("SPAN", (0, 6), (4, 6)),
        ("SPAN", (0, 7), (4, 7)),
        ("SPAN", (1, 8), (4, 8)),
        ("SPAN", (1, 9), (4, 9)),
        ("SPAN", (1, 10), (4, 10)),
        ("SPAN", (1, 11), (4, 11)),
        ("SPAN", (1, 12), (4, 12)),
        ("SPAN", (0, 13), (4, 13)),
        ("SPAN", (0, 14), (4, 14)),
        ("SPAN", (1, 15), (4, 15)),
        ("SPAN", (1, 16), (4, 16)),
        ("SPAN", (1, 17), (4, 17)),
        ("SPAN", (0, 18), (2, 18)),
        ("SPAN", (3, 18), (4, 18)),
        ("SPAN", (1, 19), (2, 19)),
        ("SPAN", (1, 20), (2, 20)),
        ("SPAN", (1, 21), (2, 21)),        
        ("SPAN", (0, 22), (2, 22)),
        ("SPAN", (0, 23), (4, 23)),
        ("SPAN", (0, 24), (4, 24)),
        ("SPAN", (0, 25), (4, 25)),
        ("SPAN", (1, 26), (4, 26)),
        ("SPAN", (1, 27), (4, 27)),
        ("SPAN", (1, 28), (4, 28)),
        ("SPAN", (0, 29), (4, 29)),
        ("SPAN", (0, 30), (4, 30)),#SOFTWARE PARA BORRADO SEGURO
        ("SPAN", (0, 31), (4, 31)),
        ("SPAN", (1, 32), (4, 32)),
        ("SPAN", (1, 33), (4, 33)),
        ("SPAN", (1, 34), (4, 34)),
        ("SPAN", (0, 35), (4, 35)),
        ("SPAN", (0, 36), (4, 36)),
        ("SPAN", (0, 37), (4, 37)),#IDENTIFICACION DE LA IMAGEN DE LA COPIA DE SEGURIDAD
        ("SPAN", (0, 38), (4, 38)),
        ("SPAN", (1, 39), (4, 39)),
        ("SPAN", (1, 40), (4, 40)),
        ("SPAN", (0, 41), (4, 41)),
        ("SPAN", (1, 42), (4, 42)),
        ("SPAN", (1, 43), (4, 43)),
        ("SPAN", (0, 44), (4, 44)),
        ("SPAN", (1, 45), (4, 46)),
        ("SPAN", (0, 47), (4, 47)),
        ("SPAN", (0, 48), (4, 48)),#PROTOCOLO REALIZADO POR CADA EQUIPO
        ("SPAN", (0, 49), (4, 49)),
        ("SPAN", (0, 50), (4, 50)),
        ("SPAN", (0, 51), (4, 51)),
        ("SPAN", (0, 52), (4, 52)),
        ("SPAN", (0, 53), (4, 53)),
        ("SPAN", (0, 54), (4, 54)),
        ("SPAN", (0, 55), (4, 55)),
        ("SPAN", (0, 56), (4, 56)),
        ("SPAN", (0, 57), (4, 57)),
        ("SPAN", (0, 58), (4, 58)),
        ("SPAN", (0, 59), (4, 59)),
        ("SPAN", (0, 60), (4, 60)),
        ("SPAN", (0, 61), (4, 61)),
        ("SPAN", (0, 62), (4, 62)),
        ("SPAN", (0, 63), (4, 63)),
        ("SPAN", (0, 64), (4, 64)),
        ("SPAN", (0, 65), (4, 65)),
        ("SPAN", (0, 66), (4, 66)),
        ("SPAN", (0, 67), (4, 67)),
        ("SPAN", (0, 68), (4, 68)),#FIRMAS
        ("SPAN", (0, 69), (4, 69)),
        ("SPAN", (0, 70), (4, 70)),
        ("SPAN", (0, 71), (4, 71)),
        ("SPAN", (1, 72), (3, 72)),
        ("SPAN", (1, 73), (3, 73)),
        ("SPAN", (1, 74), (3, 74)),
        ("SPAN", (1, 75), (3, 75)),
        ("SPAN", (1, 76), (3, 76)),
        ("SPAN", (0, 77), (4, 77)),
        ("SPAN", (0, 78), (4, 78)),#REGISTRO FOTOGRAFICO
        ("SPAN", (0, 79), (4, 79)),
        ("SPAN", (0, 80), (1, 80)),
        ("SPAN", (3, 80), (4, 80)),
        ("SPAN", (0, 81), (1, 81)),#foto1
        ("SPAN", (3, 81), (4, 81)),#foto2
        ("SPAN", (0, 82), (1, 82)),
        ("SPAN", (3, 82), (4, 82)),
        ("SPAN", (0, 83), (4, 83)),
        ("SPAN", (0, 84), (1, 84)),
        ("SPAN", (3, 84), (4, 84)),
        ("SPAN", (0, 85), (4, 85)),
        ("SPAN", (0, 86), (1, 86)),
        ("SPAN", (3, 86), (4, 86)),
        ("SPAN", (0, 87), (1, 87)),
        ("SPAN", (3, 87), (4, 87)),
        ("SPAN", (0, 88), (4, 88)),
        ("SPAN", (0, 89), (1, 89)),
        ("SPAN", (3, 89), (4, 89)),

        ("ROWHEIGHT", (0, 1), (4, 1), 5),

        ("BACKGROUND", (0, 2), (-1, 2), colors.lightgrey),
        ("ALIGN", (0, 2), (4, 2), "CENTER"),  # Centrar texto

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # Centrar verticalmente
        
        
        ("SPAN", (1, 0), (4, 0)),  # Combina desde (1, 0) hasta (4, 0)

        ("BACKGROUND", (0, 4), (-1, 4), colors.lightgrey),  # Fondo gris
        ("ALIGN", (0, 4), (4, 4), "CENTER"),  # Centrar texto

        # Estilo para Fila 2
        ("BACKGROUND", (0, 2), (-1, 2), colors.lightgrey),  # Fondo amarillo
        ("SPAN", (0, 1), (4, 1)),  # Combina desde (1, 0) hasta (4, 0)
        

        # Estilo para Fila 4
        ("BACKGROUND", (0, 4), (-1, 4), colors.lightgrey),  # Fondo gris

        # Estilo para Fila 5
        ("FONTSIZE", (0, 5), (-1, 5), 14),  # Texto más grande

        # Estilo para Fila 6
        ("ALIGN", (0, 6), (-1, 6), "CENTER"),  # Texto centrado
    ])

    tabla.setStyle(estilos)

    # Añadir tabla al documento
    elementos.append(tabla)

    # Guardar el PDF
    pdf.build(elementos)
    
    return ruta_pdf

