import os
import sys
from app import crear_app, db
from app.models import Usuario, Estado_usuario
from app.utils import reiniciar_intentos_usuario

def resetear_admin(username):
    app = crear_app()
    
    # Aseguramos la ruta absoluta a la base de datos para evitar errores de contexto
    db_path = os.path.join(os.getcwd(), 'instance', 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    with app.app_context():
        admin = Usuario.query.filter_by(userName=username).first()

        if not admin:
            print(f"\n❌ ERROR: No se encontró el usuario '{username}' en la base de datos.")
            return

        print(f"\n⚠️  ATENCIÓN: Estás a punto de desbloquear y resetear la contraseña del usuario '{username}'.")
        confirmacion = input("¿Estás seguro de que deseas continuar? (s/n): ")

        if confirmacion.lower() != 's':
            print("\n🚫 Operación cancelada por el usuario.")
            return

        try:
            # 1. Reactivar estado de la cuenta
            admin.estado = Estado_usuario.ACTIVO
            
            # 2. Asignar contraseña temporal por defecto
            admin.set_password('GrupoASD123*')
            
            # 3. Limpiar contador de intentos fallidos
            reiniciar_intentos_usuario(admin.userName)
            
            db.session.commit()

            print("\n✅ ¡OPERACIÓN EXITOSA!")
            print("-" * 30)
            print(f"👤 Usuario desbloqueado: {admin.userName}")
            print("🔑 Nueva Contraseña: GrupoASD123*")
            print("-" * 30)
            print("💡 Inicia sesión y cambia esta contraseña inmediatamente.")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Ocurrió un error al intentar actualizar la base de datos: {e}")

if __name__ == '__main__':
    print("\n" + "=" * 45)
    print(" 🛠️  PANEL DE MANTENIMIENTO DE EMERGENCIA")
    print("=" * 45)
    
    usuario_input = input("\nIngresa el 'userName' del administrador a recuperar (ej. admin): ")
    
    if usuario_input.strip():
        resetear_admin(usuario_input.strip())
    else:
        print("❌ Operación cancelada. Debes ingresar un nombre de usuario.")