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
    AGENTE = "Agente"

class Roles(Enum):
    REGISTRADURIA = "Registraduria"
    AUDITORIA = "Auditoria"
    PROCURADURIA = "Procuraduria"
    CONTRATISTA = "Contratista"
    
class EstadoEnum(Enum):
    REGISTRADO = "Registrado"
    EN_PROCESO = "En proceso"
    FINALIZADO = "Finalizado"

class Estado_usuario(Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    
class Proceso(Enum):
    CONGRESO = "CONGRESO"
    
    
# Modelo de usuario  
class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    apellido = db.Column(db.String(150), nullable=False)
    userName = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.Enum(Rol), default=Rol.AGENTE)
    password = db.Column(db.String(512), nullable=False)
    estado = db.Column(db.Enum(Estado_usuario), default=Estado_usuario.ACTIVO)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

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
class Equipo(db.Model):
    __tablename__ = "equipo"
    asd_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    # Campo ENUM para el estado
    estado = db.Column(db.Enum(EstadoEnum), default=EstadoEnum.REGISTRADO)
    direccion = db.Column(db.String(255), nullable=True)
    comision = db.Column(db.String(100), nullable=True)
    cod_comision = db.Column(db.Numeric(10, 0), nullable=True)# identificador de la comision por jal o consulta
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
    proceso = db.Column(db.Enum(Proceso), default=Proceso.CONGRESO)# cambiar campo por jal o consulta proceso
    observacion = db.Column(db.Text,nullable=True)
    fecha_hora_inicio = db.Column(db.DateTime, nullable=True)
    fecha_hora_fin = db.Column(db.DateTime, nullable=True)
    imagenes = db.Column(MutableList.as_mutable(JSON))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', name='fk_usuario_id'), nullable=False)
    
    # Relaciones con usuario
    usuario = db.relationship('Usuario', backref=db.backref('equipo', lazy=True))
        
    # Método para actualizar el estado automáticamente
    def actualizar_estado(self):
        lista_imagenes = self.imagenes if self.imagenes else []
        cantidad = len(lista_imagenes)
        
        if cantidad >= 8:
            self.estado = EstadoEnum.FINALIZADO
            if not self.fecha_hora_fin:
                self.fecha_hora_fin = datetime.now()
        elif cantidad > 0:
            self.estado = EstadoEnum.EN_PROCESO
            if not self.fecha_hora_inicio:
                self.fecha_hora_inicio = datetime.now()
        else:
            self.estado = EstadoEnum.REGISTRADO
            
        if self.nombre:
            numero = str(self.nombre).replace("ILE3-", "")
            if numero.isdigit():
                self.nombre = f"ILE3-{numero.zfill(3)}"
    
# Modelo de Actividad_verificacion
class Actividad_verificacion(db.Model):
    __tablename__ = "actividad_verificacion"
    
    asd_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Enum(EstadoEnum), default=EstadoEnum.REGISTRADO)
    
    # Datos técnicos (pueden ser diferentes a los del equipo original si se encuentra algo distinto)
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
        # Aseguramos que evidencias no sea None para evitar errores de len()
        lista_evidencias = self.evidencias if self.evidencias else []
        cantidad = len(lista_evidencias)
        
        if cantidad >= 5:
            self.estado = EstadoEnum.FINALIZADO
            if not self.fecha_hora_fin:
                self.fecha_hora_fin = datetime.now()
        elif cantidad > 0:
            self.estado = EstadoEnum.EN_PROCESO
            if not self.fecha_hora_inicio:
                self.fecha_hora_inicio = datetime.now()
        else:
            self.estado = EstadoEnum.REGISTRADO
            
        # Normalización del nombre del acta (ej: VER-ILE3-001)
        if self.nombre:
            # Quitamos cualquier prefijo previo para normalizar
            numero = "".join(filter(str.isdigit, self.nombre))
            if numero:
                self.nombre = f"VER-ILE3-{numero.zfill(3)}"
    
    
# Modelo de Representante
class Representante(db.Model):
    __tablename__ = "representante"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    rol = db.Column(db.Enum(Roles))
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
    