from reportlab.lib.pagesizes import letter# type: ignore
from reportlab.pdfgen import canvas# type: ignore
from reportlab.lib import  colors# type: ignore
from flask import current_app # Ruta base de tu aplicación
from reportlab.lib.units import inch# type: ignore
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet# type: ignore
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT# type: ignore
from reportlab.lib.units import cm# type: ignore
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image# type: ignore

def generar_pdf(nombre_archivo, equipo, representantes):        
    ruta_pdf = os.path.join(current_app.root_path, 'static', 'tmp', nombre_archivo)
    
    # Crear la carpeta si no existe
    if not os.path.exists(os.path.dirname(ruta_pdf)):
        os.makedirs(os.path.dirname(ruta_pdf))  
        
    # Logo 
    logo = os.path.join(current_app.root_path, 'static', 'img_static', 'logo_rnec.png')
    
    if os.path.exists(logo):
        logo_renc = Image(logo)
    else:
        logo_renc = Paragraph("Logo no encontrado", getSampleStyleSheet()["Normal"])
    
    # Inicializa la lista de filas para la tabla
    filas_imagenes = []
    width = 180
    height = 180
    
    # Limitar a 8 imágenes y preparar filas para la tabla
    for i in range(min(len(equipo.imagenes), 8)):
        img_name = equipo.imagenes[i]
        ruta_imagen = os.path.join(current_app.root_path, 'static', 'img', img_name)
        # Verificar si la imagen existe
        if os.path.exists(ruta_imagen):
            try:
                img = Image(ruta_imagen, width, height)
                # Agregar la imagen a la tabla
                filas_imagenes.append([img, "", img_name])  # Coloca la imagen, espacio vacío y el nombre de la imagen
            except Exception as e:
                print(f"Error al agregar imagen {img_name}: {e}")
                filas_imagenes.append(["Error al cargar la imagen", "", img_name])
        else:
            filas_imagenes.append(["Imagen no encontrada", "", img_name])
    
    # imagenes de las firmas de representantes 
   
  
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
    encabezados = [logo_renc,Paragraph("<b>ACTA INDIVIDUAL PARA LA GENERACION DE LAS IMAGENES DE LA COPIA DE SEGURIDAD DE LOS DISCOS DUROS Y BORRADO SEGURO DE EQUIPOS DE ESCRUTINIO UTILIZADOS EN LAS CONSULTAS POPULARES PARA LA CONFORMACIÓN DEL ÁREA METROPOLITANA DEL SUROCCIDENTE DE COLOMBIA Y DEL PIEDEMONTE AMAZÓNICO Y ELECCIÓN DE LAS JUNTAS ADMINISTRADORAS LOCALES (JAL) 2024.</b>", estilos["EstiloPequeno"])]
    datos = [
        [],
        [Paragraph("<b>INTRODUCCIÓN</b>", estilos["EstiloGrande"])],
        [],
        [Paragraph("<b>DESCRIPCION:</b> Esta diligencia tiene como fin ejecutar el procedimiento descrito en el memorando GI-RDE 0628  del 26 de noviembre de 2024 y el PROTOCOLO DE GENERACION DE COPIA DE SEGURIDAD DE LOS DISCOS DUROS Y BORRADO SEGURO DE LOS EQUIPOS DE COMPUTO UTILIZADOS EN LAS COMISIONES ESCRUTADORAS, aprobado por la supervisión del contrato, en cumplimiento al cronograma de actividades establecido para las Consultas Populares para la conformación del Área Metropolitana del Suroccidente de Colombia y del Piedemonte Amazónico y Elección de las Juntas Administradoras Locales (JAL) 2024 y lo estipulado en el Contrato No. 043 de 2024.",estilos["EstiloMediano"])],
        [],
        [Paragraph("<b>IDENTIFICACION DEL LUGAR DONDE SE ENCUENTRAN UBICADOS LOS EQUIPOS</b>", estilos["EstiloGrande"])],
        [""],
        ["Dirección:","Cra 10 # 17 – 72 Piso 3"],
        ["Ciudad:", "Bogotá D.C."],
        ["nombre del Edificio:","WTC I"],
        ["Fecha:", equipo.fecha_hora_inicio.strftime('%Y-%m-%d')],
        ["Hora:", equipo.fecha_hora_inicio.strftime('%H:%M:%S')],
         [],
        [Paragraph("<b>IDENTIFICACION DEL EQUIPO A EJECUTAR PROCEDIMIENTO</b>", estilos["EstiloGrande"])],
        ["Escrutinio/Comisión:", equipo.comision],
        ["Municipio:",equipo.municipio],
        ["Departamento:", equipo.departamento],
        ["EQUIPO", "", "", "DISCO DURO", ""],
        ["Marca:",equipo.equipo_marca,"","Marca:",equipo.dd_marca],
        ["Modelo:",equipo.equipo_modelo,"","Modelo:",equipo.dd_modelo],
        ["Serial:",equipo.equipo_serial,"","Capacidad:", equipo.capacidad],
        ["","","","Serial:",equipo.dd_serial],
        [],
        [Paragraph("<b>SOFTWARE PARA GENERAR IMAGEN DE LAS COPIAS DE SEGURIDAD</b>", estilos["EstiloGrande"])],
        [],
        ["Nombre del software:","FTK imager" ],
        ["Versión del software:","4.7.1.2" ],
        ["Tipo Licencia:", "FREE"],
        [],
        [Paragraph("<b>SOFTWARE PARA BORRADO SEGURO</b>", estilos["EstiloGrande"])],
        [],
        ["Nombre del software:","SHRED" ],
        ["Versión del software:","9.1" ],
        ["Tipo Licencia:", "GNU"],
        [],
        [Paragraph("<b>IDENTIFICACION DE LA IMAGEN DE LA COPIA DE SEGURIDAD</b>", estilos["EstiloGrande"])],
        [Paragraph("La copia de seguridad del equipo tendrá las siguientes características:",estilos["EstiloMediano"])],
        ["Nombre:", equipo.nombre ],
        ["HASH (SHA-1):", equipo.sha_1 ],
        ["HASH (MD5):", equipo.md5 ],
        [Paragraph("La copia de seguridad será almacenada en un medio de almacenamiento con las siguientes características: Cada disco duro debe estar marcado con una etiqueta con esta misma información",estilos["EstiloMediano"])],
        ["Marca:","SEAGATE" ],
        ["Capacidad:","18 TB" ],
        [""],
        ["Observación:",Paragraph(f"{equipo.observacion}", estilos["EstiloMediano"])],
        [],
        [],
        [Paragraph("<b>PROTOCOLO REALIZADO POR CADA EQUIPO</b>", estilos["EstiloGrande"]) ],
        [Paragraph("<b>DESCRIPCION - SE REALIZARÁ ESTE PROCEDIMIENTO DE ACUERDO CON EL LINEAMIENTO ESTABLECIDO POR LA REGISTRADURIA NACIONAL DEL ESTADO CIVIL</b>", estilos["EstiloGrande"]) ],
        [Paragraph("Identificado el equipo respectivo, al mismo se le insertará el medio de almacenamiento en el que se va a copiar imagen de la copia de seguridad",estilos["EstiloMediano"])],
        [Paragraph("Se procederá a realizar el proceso de obtención de la imagen de la copia de seguridad del disco duro del respectivo equipo de computo de escrutinio. Para lo anterior se ejecutará el programa correspondiente para la generación de la misma.",estilos["EstiloMediano"])],
        [Paragraph("Terminado el proceso se copia la imagen de la copia de seguridad al disco duro arriba mencionado.",estilos["EstiloMediano"])],
        [Paragraph("Se procederá a realizar el proceso de borrado seguro del disco duro del equipo de la comisión",estilos["EstiloMediano"])],
        [Paragraph("escrutadora. Para lo anterior se ejecutará el programa correspondiente para el borrado seguro.",estilos["EstiloMediano"]) ],
        [Paragraph("Posteriormente, se tomarán las siguientes fotos del proceso: (Dichas fotos se anexaran a la presente acta.)",estilos["EstiloMediano"])],
        [],
        [],
        [Paragraph("1.    Foto de la caja del equipo ",estilos["EstiloMediano"]) ],
        [Paragraph("2.    Foto del equipo",estilos["EstiloMediano"])],
        [Paragraph("3.    Foto serial del equipo ",estilos["EstiloMediano"])],
        [Paragraph("4.    Foto de la Identificación de la comisión",estilos["EstiloMediano"])],
        [Paragraph("5.    Foto inicio de generación de la imagen de la copia de seguridad ",estilos["EstiloMediano"])],
        [Paragraph("6.    Foto finalización de la generación de la imagen de la copia de seguridad ",estilos["EstiloMediano"])],
        [Paragraph("7.    Foto inicio del borrado ",estilos["EstiloMediano"]) ],
        [Paragraph("8.    Foto finalización del borrado",estilos["EstiloMediano"])],
        [],
        [],
        [Paragraph("<b>FIRMAS</b>", estilos["EstiloGrande"])],
        [Paragraph(f"Para constancia se firma en formato PDF con firma digita {equipo.fecha_hora_fin.strftime('%H:%M:%S')}  {equipo.fecha_hora_fin.strftime('%Y-%m-%d')} por quienes en ella intervienen",estilos["EstiloMediano"])],
        [Paragraph("Observaciones: Para dar claridad en la nitidez de las fotos se adjunta medio magnético al acta de cierre con la consolidación del registro fotográfico tomado por cada copia de seguridad",estilos["EstiloMediano"])],
        [],
        [f"Rep. {representantes[0].rol.value}", f"Nombre: {representantes[0].nombre}", "XXXXXXXX"],
        [f"Rep. {representantes[1].rol.value}", f"Nombre: {representantes[1].nombre}", "XXXXXXXX"],
        [f"Rep. {representantes[2].rol.value}", f"Nombre: {representantes[2].nombre}", "XXXXXXXX"],
        [f"Rep. {representantes[3].rol.value}", f"Nombre: {representantes[3].nombre}", "XXXXXXXX"],
        ["","", ""],
        [],
        ["REGISTRO FOTOGRAFICO" ],
        [],
        [filas_imagenes[0][0] if len(filas_imagenes) > 0 else "Sin imagen", "", "", filas_imagenes[1][0] if len(filas_imagenes) > 1 else "Sin imagen", ""],
        [Paragraph("<b>1. Foto de la caja del equipo</b>", estilos["EstiloPequeno"]), "", "", Paragraph("<b>2. Foto del equipo</b>", estilos["EstiloPequeno"])],
        [],
        [filas_imagenes[2][0] if len(filas_imagenes) > 2 else "Sin imagen", "", "", filas_imagenes[3][0] if len(filas_imagenes) > 3 else "Sin imagen", ""],
        [Paragraph("<b>3. Foto serial del equipo</b>", estilos["EstiloPequeno"]), "", "", Paragraph("<b>4. Foto de la Identificación de la comisión</b>", estilos["EstiloPequeno"])],
        [],
        [filas_imagenes[4][0] if len(filas_imagenes) > 4 else "Sin imagen", "", "", filas_imagenes[5][0] if len(filas_imagenes) > 5 else "Sin imagen", ""],
        [Paragraph("5. Foto inicio de generación de la imagen de la copia de seguridad ",estilos["EstiloMediano"]), "", "", Paragraph("6. Foto finalización de la generación de la imagen de la copia de seguridad",estilos["EstiloMediano"])],
        [],
        [filas_imagenes[6][0] if len(filas_imagenes) > 6 else "Sin imagen", "", "", filas_imagenes[7][0] if len(filas_imagenes) > 7 else "Sin imagen", ""],
        [Paragraph("<b>7. Foto inicio del borrado</b>", estilos["EstiloPequeno"]), "", "", Paragraph("<b>8. Foto finalización del borrado</b>", estilos["EstiloPequeno"])]        
    ]
    
    data_tabla = [encabezados] + datos  # Combinar encabezados y datos

    # Crear la tabla
    tabla = Table(data_tabla, colWidths = [132, 132, 24, 132, 132],rowHeights=[60, 3, 16, 3, 80, 3, 16, 3, 16, 16, 16, 16, 16, 3, 16, 16, 16, 16, 16, 16, 16, 16, 16, 3, 16, 3,16, 16, 16,3,16, 3, 16,16, 16, 2, 15, 15, 15,15,15, 30, 16,16, 0, 15,15, 2, 16, 30, 30, 30, 16,16, 16, 16,2, 2, 16,16,16, 16, 16,16, 16, 16,3, 3, 16, 16,30, 2, 25,25, 25, 25,25, 2, 16,2,190, 16, 5,200, 16, 5,200, 30, 5,200,16])

    # Aplicar estilos
    estilos = TableStyle([
        # Estilo general
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),  # Bordes
        # combinacion de celdas
        ("SPAN", (1, 0), (4, 0)),  #titulo formato
        ("SPAN", (0, 1), (4, 1)),
        ("SPAN", (0, 2), (4, 2)),  #introduccion
        ("SPAN", (0, 3), (4, 3)),  
        ("SPAN", (0, 4), (4, 4)), 
        ("SPAN", (0, 5), (4, 5)),
        ("SPAN", (0, 6), (4, 6)),#IDENTIFICACION DEL LUGAR DONDE SE ENCUENTRAN UBICADOS LOS EQUIPOS
        ("SPAN", (0, 7), (4, 7)),
        ("SPAN", (1, 8), (4, 8)),
        ("SPAN", (1, 9), (4, 9)),
        ("SPAN", (1, 10), (4, 10)),
        ("SPAN", (1, 11), (4, 11)),
        ("SPAN", (1, 12), (4, 12)),
        ("SPAN", (0, 13), (4, 13)),
        ("SPAN", (0, 14), (4, 14)),#IDENTIFICACION DEL EQUIPO A EJECUTAR PROCEDIMIENTO
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
        ("SPAN", (0, 24), (4, 24)),#SOFTWARE PARA GENERAR IMAGEN DE LAS COPIAS DE SEGURIDAD
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
        ("SPAN", (0, 36), (4, 36)),#IDENTIFICACION DE LA IMAGEN DE LA COPIA DE SEGURIDAD
        ("SPAN", (0, 37), (4, 37)),
        ("SPAN", (1, 38), (4, 38)),
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
        ("SPAN", (0, 83), (1, 83)),
        ("SPAN", (3, 83), (4, 83)),
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
        ("SPAN", (0, 90), (1, 90)),
        ("SPAN", (3, 90), (4, 90)),
        
        #Fondos de Filas
        ("BACKGROUND", (0, 2), (4, 2), colors.lightgrey),
        ("BACKGROUND", (0, 6), (4, 6), colors.lightgrey),
        ("BACKGROUND", (1, 8), (4, 8), colors.lightgrey),
        ("BACKGROUND", (1, 9), (4, 9), colors.lightgrey),
        ("BACKGROUND", (1, 10), (4, 10), colors.lightgrey),
        ("BACKGROUND", (1, 11), (4, 11), colors.lightgrey),
        ("BACKGROUND", (1, 12), (4, 12), colors.lightgrey),
        ("BACKGROUND", (0, 14), (4, 14), colors.lightgrey),
        ("BACKGROUND", (1, 15), (4, 15), colors.lightgrey),
        ("BACKGROUND", (1, 16), (4, 16), colors.lightgrey),
        ("BACKGROUND", (1, 17), (4, 17), colors.lightgrey),
        ("BACKGROUND", (1, 19), (2, 19), colors.lightgrey),
        ("BACKGROUND", (4, 19), (4, 19), colors.lightgrey),
        ("BACKGROUND", (1, 20), (2, 20), colors.lightgrey),
        ("BACKGROUND", (4, 20), (4, 20), colors.lightgrey),
        ("BACKGROUND", (1, 21), (2, 21), colors.lightgrey),
        ("BACKGROUND", (4, 21), (4, 21), colors.lightgrey),
        ("BACKGROUND", (4, 22), (4, 22), colors.lightgrey),
        ("BACKGROUND", (0, 24), (4, 24), colors.lightgrey),
        ("BACKGROUND", (1, 26), (4, 26), colors.lightgrey),
        ("BACKGROUND", (1, 27), (4, 27), colors.lightgrey),
        ("BACKGROUND", (1, 28), (4, 28), colors.lightgrey),
        ("BACKGROUND", (0, 30), (4, 30), colors.lightgrey),
        ("BACKGROUND", (1, 32), (4, 32), colors.lightgrey),
        ("BACKGROUND", (1, 33), (4, 33), colors.lightgrey),
        ("BACKGROUND", (1, 34), (4, 34), colors.lightgrey),
        ("BACKGROUND", (0, 36), (4, 36), colors.lightgrey),
        ("BACKGROUND", (1, 38), (4, 38), colors.lightgrey),
        ("BACKGROUND", (1, 39), (4, 39), colors.lightgrey),
        ("BACKGROUND", (1, 40), (4, 40), colors.lightgrey),
        ("BACKGROUND", (1, 42), (4, 42), colors.lightgrey),
        ("BACKGROUND", (1, 43), (4, 43), colors.lightgrey),
        ("BACKGROUND", (0, 48), (4, 48), colors.lightgrey),
        ("BACKGROUND", (0, 68), (4, 68), colors.lightgrey),
        ("BACKGROUND", (0, 78), (4, 78), colors.lightgrey),
    ])

    tabla.setStyle(estilos)

    # Añadir tabla al documento
    elementos.append(tabla)

    # Guardar el PDF
    pdf.build(elementos)
    
    return ruta_pdf


