from datetime import datetime
from flask_login import UserMixin
from app import login
from werkzeug.security import generate_password_hash,check_password_hash;
from app import db
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy import event
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
        """
        Normaliza el nombre del equipo al formato ILE3-XXX.
        
        Garantiza idempotencia: ejecutar múltiples veces produce el mismo resultado.
        Evita concatenación accidental de dígitos del prefijo con el número.
        """
        if self.nombre:
            import re
            nombre_str = str(self.nombre).strip()
            
            # Validar si ya está en el formato correcto (ILE3-\d+)
            if not re.match(r'^ILE3-\d+$', nombre_str):
                # Necesita normalización
                numero = None
                
                # Si ya contiene "ILE3", extraer solo el número que viene después
                # Esto evita incluir el "3" del prefijo
                if 'ILE3' in nombre_str.upper():
                    # Buscar patrón: ILE3 seguido opcionalmente de espacios/guión y luego dígitos
                    match = re.search(r'ILE3\s*-?\s*(\d+)', nombre_str.upper())
                    if match:
                        numero = match.group(1)
                    else:
                        # Fallback: si no hay patrón claro, extraer todos los dígitos
                        numero = re.sub(r'\D', '', nombre_str)
                else:
                    # No contiene ILE3: extraer todos los dígitos (comportamiento original)
                    numero = re.sub(r'\D', '', nombre_str)
                
                # Formatear el número con padding mínimo de 3 dígitos
                if numero:
                    # zfill garantiza mínimo 3 dígitos, mantiene números más largos
                    numero = numero.zfill(3)
                    self.nombre = f"ILE3-{numero}"

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
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    
    # -------------------------------------------------------------------------
    # Tiempos Lógicos y Evidencias Fotográficas (Exclusivos del Acta)
    # -------------------------------------------------------------------------
    fecha_hora_inicio = db.Column(
        db.DateTime, 
        nullable=True, 
        comment="Captura el momento exacto en que se sube la primera imagen al JSON."
    )
    fecha_hora_fin = db.Column(
        db.DateTime, 
        nullable=True, 
        comment="Captura el momento exacto en que se completa el flujo (7/7 imágenes)."
    )
    
    # MutableList permite que SQLAlchemy detecte cambios internos al hacer appends o modificaciones por índice
    evidencias = db.Column(MutableList.as_mutable(JSON), default=[None] * 7)
    
    # -------------------------------------------------------------------------
    # Auditoría Estándar del Sistema (Persistencia en Base de Datos)
    # -------------------------------------------------------------------------
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # -------------------------------------------------------------------------
    # Relación Unívoca con el Equipo (Single Source of Truth)
    # -------------------------------------------------------------------------
    # unique=True y uselist=False garantizan una relación estricta de 1 a 1 en el flujo
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipo.asd_id', name='fk_equipo_id'), nullable=False, unique=True)
    
    equipo = db.relationship(
        'Equipo', 
        foreign_keys=[equipo_id],
        backref=db.backref('actividad_asociada', uselist=False, lazy=True)
    )

    activo = db.Column(db.Boolean, default=True, nullable=False)

    # -------------------------------------------------------------------------
    # Propiedad Dinámica: Consumo del Estado
    # -------------------------------------------------------------------------
    @property
    def estado(self):
        """
        Puente dinámico hacia el módulo de Equipos. Permite que WeasyPrint, el backend 
        y las vistas lean 'actividad.estado' sin tener una columna duplicada en BD.
        """
        if self.equipo:
            return self.equipo.estado
        return EstadoEnum.REGISTRADO

    # -------------------------------------------------------------------------
    # Lógica Autónoma de Auditoría de Tiempos por Imágenes
    # -------------------------------------------------------------------------
    def registrar_tiempos_evidencias(self):
        """
        Analiza el estado posicional del arreglo JSON de imágenes para fijar 
        las marcas de tiempo lógicas de la verificación.
        """
        lista_imgs = self.evidencias if self.evidencias else []
        
        # Conteo real de imágenes cargadas (excluyendo vacíos y nulos)
        cantidad_reales = sum(1 for img in lista_imgs if img is not None and str(img).strip() != "")

        # HITO A: Detectar el inicio de la operación en laboratorio (Primera foto cargada)
        if cantidad_reales > 0 and not self.fecha_hora_inicio:
            self.fecha_hora_inicio = datetime.now()

        # HITO B: Detectar el cierre definitivo (Se completaron las 7 evidencias requeridas)
        if cantidad_reales == 7 and not self.fecha_hora_fin:
            self.fecha_hora_fin = datetime.now()
            
        # HITO C: Resiliencia/Retroceso (Si el Administrador remueve fotos, el fin se libera)
        elif cantidad_reales < 7 and self.fecha_hora_fin:
            self.fecha_hora_fin = None

    def todas_evidencias_completas(self):
        """
        Verifica si las 7 imágenes/evidencias están completamente cargadas.
        Retorna True solo si todos los 7 slots contienen datos válidos.
        """
        if not self.evidencias or len(self.evidencias) < 7:
            return False
        
        # Contar imágenes válidas (no nulas y no vacías)
        cantidad_validas = sum(1 for img in self.evidencias if img is not None and str(img).strip() != "")
        
        return cantidad_validas == 7

    def puede_generar_pdf(self):
        """
        Determina si se puede generar el PDF basado en:
        1. Que NO esté en estado PENDIENTE_HASH o PENDIENTE_LOG
        2. Que las 7 imágenes estén completas
        """
        if not self.equipo:
            return False
        
        # Verificar que NO esté en estados pendientes
        estado_bloqueado = self.equipo.estado in [
            EstadoEnum.PENDIENTE_HASH,
            EstadoEnum.PENDIENTE_LOG
        ]
        
        if estado_bloqueado:
            return False
        
        # Verificar que todas las evidencias estén completas
        return self.todas_evidencias_completas()

    def __repr__(self):
        return f"<Actividad_verificacion ID: {self.id} | Equipo_ID: {self.equipo_id} | Estado: {self.estado.value}>"


# -------------------------------------------------------------------------
# Escuchadores Automatizados (SQLAlchemy Listeners)
# -------------------------------------------------------------------------
@event.listens_for(Actividad_verificacion, 'before_insert')
@event.listens_for(Actividad_verificacion, 'before_update')
def ejecutar_auditoria_de_tiempos(mapper, connection, target):
    """
    Garantiza que el análisis de slots fotográficos se ejecute automáticamente 
    siempre, justo antes de enviar los datos físicos a MySQL/PostgreSQL.
    Evita tener que llamar el método manualmente en el controlador de rutas.
    """
    target.registrar_tiempos_evidencias()
    
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