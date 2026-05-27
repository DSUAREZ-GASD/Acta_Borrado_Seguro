from app.models import Actividad_verificacion, EstadoEnum
from app import db

def ejecutar_replica_a_verificacion(equipo):
    """
    Toma un equipo validado, verifica si requiere acta de verificación
    y genera una copia exacta de sus metadatos lógicos y de hardware,
    dejando el contenedor de imágenes limpio.
    """
    # Si no es equipo de verificación o ya fue replicado antes, se cancela la acción
    if not equipo.es_verificacion or equipo.replica_ejecutada:
        return None

    try:
        # Construimos el acta de verificación cruzando la información del equipo original
        nueva_actividad = Actividad_verificacion(
            nombre=equipo.nombre,  # El formateador interno lo convertirá en VER-ILE3-XXX
            estado=EstadoEnum.REGISTRADO,
            
            # Ubicación geográfica e institucional
            direccion=equipo.direccion,
            comision=equipo.comision,
            cod_comision=equipo.cod_comision,
            capacidad=equipo.capacidad,
            municipio=equipo.municipio,
            departamento=equipo.departamento,
            
            # Datos duros de Hardware
            equipo_marca=equipo.equipo_marca,
            equipo_modelo=equipo.equipo_modelo,
            equipo_serial=equipo.equipo_serial,
            dd_marca=equipo.dd_marca,
            dd_modelo=equipo.dd_modelo,
            dd_serial=equipo.dd_serial,
            
            # Integridad Lógica (Hashes)
            sha_1=equipo.sha_1,
            md5=equipo.md5,
            proceso=equipo.proceso,
            
            # Control de asignación y auditoría
            usuario_id=equipo.usuario_id,  # El mismo operador que consolida el equipo
            examinador_id=None,            # Queda en blanco para asignación posterior en Mesa de Control
            
            # REGLA ESTRICTA: Las imágenes difieren entre módulos, se inicializa vacío
            evidencias=[]                  
        )
        
        # Ejecutamos su formateador de nombres y estados por defecto
        nueva_actividad.actualizar_estado()
        
        # Agregamos al contexto de la transacción
        db.session.add(nueva_actividad)
        
        # Marcamos el escudo en el equipo original para evitar duplicados en futuras ediciones
        equipo.replica_ejecutada = True
        
        return nueva_actividad

    except Exception as e:
        raise RuntimeError(f"Fallo en la replicación automática de datos de Grupo ASD: {str(e)}")