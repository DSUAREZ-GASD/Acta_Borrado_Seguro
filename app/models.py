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
    
# Modelo de usuario  
class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.Enum(Rol), default=Rol.AGENTE)
    password = db.Column(db.String(128), nullable=False)
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
    comision = db.Column(db.String(100), nullable=True)
    municipio = db.Column(db.String(100), nullable=True)
    departamento = db.Column(db.String(100), nullable=True)
    equipo_marca = db.Column(db.String(100), nullable=True)
    equipo_modelo = db.Column(db.String(100), nullable=True)
    equipo_serial = db.Column(db.String(100), nullable=True)
    dd_marca = db.Column(db.String(100), nullable=True)
    dd_modelo = db.Column(db.String(100), nullable=True)
    dd_serial = db.Column(db.String(100), nullable=True)
    sha_1 = db.Column(db.String(100), nullable=True)
    md_5 = db.Column(db.String(100), nullable=True)
    observacion = db.Column(db.Text,nullable=True)
    fecha_hora_fin = db.Column(db.DateTime, nullable=True)
    imagenes = db.Column(MutableList.as_mutable(JSON))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', name='fk_usuario_id'), nullable=False)
    
    usuario = db.relationship('Usuario', backref=db.backref('equipo', lazy=True))
    
    # Método para actualizar el estado automáticamente
    def actualizar_estado(self):
        if len(self.imagenes) >= 8:
            self.estado = EstadoEnum.FINALIZADO
            self.fecha_hora_fin = datetime.now()
        elif len(self.imagenes) > 0:
            self.estado = EstadoEnum.EN_PROCESO
        else:
            self.estado = EstadoEnum.REGISTRADO

# Modelo de Representante
class Representante(db.Model):
    __tablename__ = "representante"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    rol = db.Column(db.Enum(Roles))
    firma = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
