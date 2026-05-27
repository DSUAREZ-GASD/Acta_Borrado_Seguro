from datetime import datetime
from flask_login import UserMixin
from app import login
from werkzeug.security import generate_password_hash,check_password_hash;
from app import db
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.mysql import JSON
from enum import Enum
# Modelos
# Columnas de atributos enumerados
class Rol(Enum):
    ADMINISTRADOR = "Administrador"
    AGENTE_OPERADOR = "Agente_1"   # Sube imágenes y edita datos sin reemplazar
    AGENTE_SUPERVISOR = "Agente_2" # Sube, edita y reemplaza imágenes
    AGENTE_AUDITOR = "Agente_3"    # Edita datos, hashes, logs y genera PDFs

class EntidadRepresentante(Enum):
    REGISTRADURIA = "Registraduria"
    AUDITORIA = "Auditoria"
    PROCURADURIA = "Procuraduria"
    CONTRATISTA = "Contratista"
    
class EstadoEnum(Enum):
    REGISTRADO = "REGISTRADO"
    GESTION_ADMINISTRADOR = "GESTIÓN ADMINISTRADOR"  # Rama izquierda: Equipo es Maestro
    PENDIENTE_HASH = "PENDIENTE HASH"                # Esperando validación de firmas digitales
    PENDIENTE_LOG = "PENDIENTE LOG"                  # Esperando el reporte obligatorio de borrado
    PENDIENTE_FASE_2 = "PENDIENTE FASE 2"            # Esperando completitud de fotos (caja equipo/fin copia)
    EN_PROCESO = "EN PROCESO"
    FINALIZADO = "FINALIZADO"

class Estado_usuario(Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    
class Proceso(Enum):
    CONGRESO = "CONGRESO"
    

MATRIZ_PERMISOS = {
    Rol.ADMINISTRADOR: {
        "subir_imagenes": True,
        "reemplazar_imagenes": True,
        "eliminar_imagenes": True,
        "escribir_datos": True,
        "ver_hash_y_logs": True,
        "generar_pdf": True,
        "gestionar_roles": True
    },
    Rol.AGENTE_OPERADOR: { # Agente 1
        "subir_imagenes": True,
        "reemplazar_imagenes": False,
        "eliminar_imagenes": False,
        "escribir_datos": True,
        "ver_hash_y_logs": False,
        "generar_pdf": False,
        "gestionar_roles": False
    },
    Rol.AGENTE_SUPERVISOR: { # Agente 2
        "subir_imagenes": True,
        "reemplazar_imagenes": True,
        "eliminar_imagenes": False,
        "escribir_datos": True,
        "ver_hash_y_logs": False,
        "generar_pdf": False,
        "gestionar_roles": False
    },
    Rol.AGENTE_AUDITOR: { # Agente 3
        "subir_imagenes": True,
        "reemplazar_imagenes": True,
        "eliminar_imagenes": False,
        "escribir_datos": True,
        "ver_hash_y_logs": True,
        "generar_pdf": True,
        "gestionar_roles": False
    }
}
    
    
# Modelo de usuario  
class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    apellido = db.Column(db.String(150), nullable=False)
    userName = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Modifica la línea de 'rol' en tu clase Usuario:
    rol = db.Column(db.Enum(Rol, values_callable=lambda x: [e.value for e in x]), default=Rol.AGENTE_OPERADOR)
    password = db.Column(db.String(512), nullable=False)
    estado = db.Column(db.Enum(Estado_usuario), default=Estado_usuario.ACTIVO)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def tiene_permiso(self, capacidad):
        permisos_rol = MATRIZ_PERMISOS.get(self.rol, {})
        return permisos_rol.get(capacidad, False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, clave):
        return check_password_hash(self.password, clave)
    
    def __repr__(self):
        return f'<Usuario {self.userName}>'
    
@login.user_loader
def user_loader(id):
    return Usuario.query.get(id)
 
 
# Modelo de Equipo
# Modelo de Equipo
class Equipo(db.Model):
    __tablename__ = "equipo"
    asd_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Enum(EstadoEnum), default=EstadoEnum.REGISTRADO)
    direccion = db.Column(db.String(255), nullable=True)
    comision = db.Column(db.String(100), nullable=True)
    cod_comision = db.Column(db.Numeric(10, 0), nullable=True)
    capacidad = db.Column(db.String(100), nullable=True)
    municipio = db.Column(db.String(100), nullable=True)
    departamento = db.Column(db.String(100), nullable=True)
    equipo_marca = db.Column(db.String(100), nullable=True)
    equipo_modelo = db.Column(db.String(100), nullable=True)
    equipo_serial = db.Column(db.String(100), nullable=True)
    dd_marca = db.Column(db.String(100), nullable=True)
    dd_modelo = db.Column(db.String(100), nullable=True)
    dd_serial = db.Column(db.String(100), nullable=True)
    dd_marca_bk = db.Column(db.String(100), nullable=True)
    dd_serial_bk = db.Column(db.String(100), nullable=True)
    dd_capacidad_bk = db.Column(db.String(100), nullable=True)
    sha_1 = db.Column(db.String(100), nullable=True)
    md5 = db.Column(db.String(100), nullable=True)
    proceso = db.Column(db.Enum(Proceso), default=Proceso.CONGRESO)
    observacion = db.Column(db.Text, nullable=True)
    fecha_hora_inicio = db.Column(db.DateTime, nullable=True)
    fecha_hora_fin = db.Column(db.DateTime, nullable=True)
    imagenes = db.Column(MutableList.as_mutable(JSON))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', name='fk_usuario_id'), nullable=False)
    
    # ---------------------------------------------------------
    # NUEVOS CAMPOS DE CONTROL DE FLUJO (Paso 1)
    # ---------------------------------------------------------
    es_maestro = db.Column(db.Boolean, default=False, nullable=False)
    es_verificacion = db.Column(db.Boolean, default=False, nullable=False)
    replica_ejecutada = db.Column(db.Boolean, default=False, nullable=False) # Evita duplicación infinita en el Paso 4
    
    # Relaciones con usuario
    usuario = db.relationship('Usuario', backref=db.backref('equipo', lazy=True))
        
    # Método para actualizar el estado automáticamente (Integrado con el Flujo Dinámico)
    def actualizar_estado(self):
        # ... Tu lógica para normalizar el nombre (ILE3-XXX) ...

        # Importación perezosa
        from app.utils.evaluador_flujo import evaluar_estado_equipo
        
        # OJO AQUÍ: Desempaquetamos la tupla en dos variables independientes
        nuevo_estado, _msg = evaluar_estado_equipo(self)
        
        # Asignamos ÚNICAMENTE el Enum limpio a la columna de la base de datos
        self.estado = nuevo_estado

        # Control de marcas de tiempo automáticas
        if self.estado == EstadoEnum.FINALIZADO and not self.fecha_hora_fin:
            self.fecha_hora_fin = datetime.now()
        elif self.estado in [EstadoEnum.EN_PROCESO, EstadoEnum.PENDIENTE_HASH, EstadoEnum.PENDIENTE_LOG, EstadoEnum.PENDIENTE_FASE_2] and not self.fecha_hora_inicio:
            self.fecha_hora_inicio = datetime.now()
    
# Modelo de Actividad_verificacion
class Actividad_verificacion(db.Model):
    __tablename__ = "actividad_verificacion"
    
    asd_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Enum(EstadoEnum), default=EstadoEnum.REGISTRADO)
    
    # Datos técnicos (pueden ser diferentes a los del equipo original si se encuentra algo distinto)
    observacion = db.Column(db.Text, nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    comision = db.Column(db.String(100), nullable=True)
    cod_comision = db.Column(db.Numeric(10, 0), nullable=True)
    capacidad = db.Column(db.String(100), nullable=True)
    municipio = db.Column(db.String(100), nullable=True)
    departamento = db.Column(db.String(100), nullable=True)
    
    # Información del hardware verificado
    equipo_marca = db.Column(db.String(100), nullable=True)
    equipo_modelo = db.Column(db.String(100), nullable=True)
    equipo_serial = db.Column(db.String(100), nullable=True)
    dd_marca = db.Column(db.String(100), nullable=True)
    dd_modelo = db.Column(db.String(100), nullable=True)
    dd_serial = db.Column(db.String(100), nullable=True)
    
    # Seguridad y proceso
    sha_1 = db.Column(db.String(100), nullable=True)
    md5 = db.Column(db.String(100), nullable=True)
    proceso = db.Column(db.Enum(Proceso), default=Proceso.CONGRESO)
    
    # Tiempos y evidencias
    fecha_hora_inicio = db.Column(db.DateTime, nullable=True)
    fecha_hora_fin = db.Column(db.DateTime, nullable=True)
    evidencias = db.Column(MutableList.as_mutable(JSON), default=[])
    
    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones con usuario
    examinador_id = db.Column(db.Integer, db.ForeignKey('usuario.id', name='fk_examinador_id'), nullable=True)
    examinador_rel = db.relationship(
        'Usuario', 
        foreign_keys=[examinador_id], # <--- Indicar la llave específica
        backref=db.backref('actividades_examinadas', lazy=True) # <--- Nombre único para el backref
    )
    
    # Relación con el usuario que verifica
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', name='fk_verificador_id'), nullable=False)
    usuario = db.relationship(
        'Usuario', 
        foreign_keys=[usuario_id], # <--- Indicar la llave específica
        backref=db.backref('actividades_creadas', lazy=True) # <--- Nombre único para el backref
    )

    def actualizar_estado(self):
        # 1. Normalización del nombre del acta (ej: VER-ILE3-001)
        if self.nombre:
            numero = "".join(filter(str.isdigit, str(self.nombre)))
            if numero:
                self.nombre = f"VER-ILE3-{numero.zfill(3)}"

        # 2. Consumo de la Máquina de Estados Pasiva
        from app.utils.evaluador_flujo import evaluar_estado_verificacion
        nuevo_estado, _mensaje = evaluar_estado_verificacion(self)
        
        # Asignamos estrictamente el Enum para que MySQL no trunque los datos
        self.estado = nuevo_estado
        
        # 3. Gestión automática de marcas de tiempo lógicas
        from datetime import datetime
        if self.estado == EstadoEnum.FINALIZADO and not self.fecha_hora_fin:
            self.fecha_hora_fin = datetime.now()
        elif self.estado in [EstadoEnum.EN_PROCESO, EstadoEnum.PENDIENTE_HASH, EstadoEnum.PENDIENTE_LOG, EstadoEnum.PENDIENTE_FASE_2] and not self.fecha_hora_inicio:
            self.fecha_hora_inicio = datetime.now()
    
# Modelo de Representante
class Representante(db.Model):
    __tablename__ = "representante"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    rol = db.Column(db.Enum(EntidadRepresentante))
    firma = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    

class ActaConfig(db.Model):
    __tablename__="acta_config"
    id = db.Column(db.Integer, primary_key=True)
    tipo_acta = db.Column(db.String(50), nullable=False)
    campo_sistema = db.Column(db.String(100), nullable=False)
    etiqueta_pdf = db.Column(db.String(100), nullable=False)
    es_visible = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<ActaConfig {self.tipo_acta} - {self.campo_sistema}>'