from flask import render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.dashboard import dashboard_bp
from app.utils import acceso_requerido
from app.models import Equipo, Usuario, EstadoEnum
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

@dashboard_bp.route('/dashboard-admin')
@acceso_requerido(roles=["Administrador", "Agente_3"])
@login_required
def dashboard_admin():
    total_equipos = db.session.query(func.count(Equipo.asd_id)).scalar() or 0
    total_usuarios = db.session.query(func.count(Usuario.id)).scalar() or 0
    
    # --- LOGICA EXISTENTE DE LOS 7 DIAS (LINEA) ---
    hoy = datetime.now().date()
    hace_7_dias = hoy - timedelta(days=6)
    linea_labels = []
    linea_data = []
    for i in range(7):
        fecha = hace_7_dias + timedelta(days=i)
        linea_labels.append(fecha.strftime('%d/%m'))
        count = db.session.query(func.count(Equipo.asd_id)).filter(func.date(Equipo.created_at) == fecha).scalar() or 0
        linea_data.append(count)
    
    # --- LOGICA EXISTENTE DEL GRAFICO DE TORTA ---
    conteos_estado = db.session.query(Equipo.estado, func.count(Equipo.asd_id)).group_by(Equipo.estado).all()
    pendientes = 0
    en_proceso = 0
    completados = 0
    
    # --- NUEVA LOGICA: AVANCE POR ESTADOS INDIVIDUALES ---
    # Inicializamos un diccionario con la estructura y colores corporativos asignados por fase
    config_estados = {
        EstadoEnum.REGISTRADO: {"nombre": "Registrado", "color": "bg-secondary"},
        EstadoEnum.GESTION_ADMINISTRADOR: {"nombre": "Gestión Administrador", "color": "bg-orange-custom", "style": "background-color: #fd7e14;"}, # Fallback color
        EstadoEnum.PENDIENTE_HASH: {"nombre": "Pendiente Validación Hash", "color": "bg-info"},
        EstadoEnum.PENDIENTE_LOG: {"nombre": "Pendiente Reporte Log", "color": "bg-dark"},
        EstadoEnum.PENDIENTE_FASE_2: {"nombre": "Pendiente Evidencia Fase 2", "color": "bg-warning"},
        EstadoEnum.FINALIZADO: {"nombre": "Finalizado", "color": "bg-success"}
    }
    
    # Estructuramos el diccionario que irá al frontend con conteos inicializados en 0
    estados_progreso = {
        enum_obj: {
            "nombre": info["nombre"],
            "color": info["color"],
            "style": info.get("style", ""),
            "conteo": 0,
            "porcentaje": 0.0
        } for enum_obj, info in config_estados.items()
    }
    
    # Procesamos los resultados reales de la Base de Datos
    for estado, total in conteos_estado:
        if estado in estados_progreso:
            estados_progreso[estado]["conteo"] = total
            if total_equipos > 0:
                # Cálculo de porcentaje con un decimal
                estados_progreso[estado]["porcentaje"] = round((total / total_equipos) * 100, 1)
        
        # Mantenemos la lógica de acumulación de la Torta
        if estado == EstadoEnum.REGISTRADO: pendientes += total
        elif estado == EstadoEnum.FINALIZADO: completados += total
        elif estado: en_proceso += total

    torta_labels = ["Pendiente", "En Proceso", "Completado"]
    torta_data = [pendientes, en_proceso, completados]
    
    return render_template('dashboard/dashboard.html',
                           total_equipos=total_equipos,
                           total_usuarios=total_usuarios,
                           linea_labels=linea_labels,
                           linea_data=linea_data,
                           torta_labels=torta_labels,
                           torta_data=torta_data,
                           estados_progreso=estados_progreso)