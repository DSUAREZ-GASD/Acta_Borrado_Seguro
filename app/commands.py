# app/commands.py
import click
from flask.cli import with_appcontext
from app import db

@click.command('sync-pdf-configs')
@with_appcontext
def sync_pdf_configs():
    """Puebla la tabla ActaConfig basándose en los modelos de Equipo y Verificación."""
    from app.models import Equipo, Actividad_verificacion, ActaConfig
    
    # Mapeo de modelos y sus tipos para el PDF
    mapeo = [
        (Equipo, 'borrado'),
        (Actividad_verificacion, 'verificacion')
    ]
    
    # Columnas que ignoraremos (no tienen sentido en el PDF)
    excluidas = {
        'asd_id', 'id', 'created_at', 'updated_at', 'usuario_id', 
        'estado', 'imagenes', 'evidencias', 'nombre'
    }

    click.echo("Iniciando sincronización de campos...")

    for modelo, tipo in mapeo:
        for col in modelo.__table__.columns:
            if col.name not in excluidas:
                # Si no existe, lo creamos
                existe = ActaConfig.query.filter_by(
                    tipo_acta=tipo, 
                    campo_sistema=col.name
                ).first()
                
                if not existe:
                    nueva_conf = ActaConfig(
                        tipo_acta=tipo,
                        campo_sistema=col.name,
                        etiqueta_pdf=col.name.replace('_', ' ').title(),
                        es_visible=True,
                        orden=10
                    )
                    db.session.add(nueva_conf)
                    click.echo(f"  [+] Campo registrado: {tipo} -> {col.name}")
    
    db.session.commit()
    click.echo("¡Sincronización completada exitosamente!")