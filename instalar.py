from app import crear_app, db
from app.models import Usuario, Rol, Estado_usuario

def instalacion_limpia():
    app = crear_app()
    with app.app_context():
        # 1. Crear todas las tablas desde cero
        db.create_all()
        
        # 2. Crear el usuario Administrador por defecto
        admin = Usuario(
            nombre='Administrador',
            apellido='Inicial',
            userName='admin',
            email='admin@grupoasd.com',
            rol=Rol.ADMINISTRADOR,
            estado=Estado_usuario.ACTIVO
        )
        # La contraseña temporal
        admin.set_password('GrupoASD123*')
        
        db.session.add(admin)
        db.session.commit()
        print("✅ Base de datos reconstruida con éxito.")
        print("🔑 Usuario: admin | Contraseña: GrupoASD123*")

if __name__ == '__main__':
    instalacion_limpia()