from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    """Factory pattern para crear la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Registrar blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.routes.alumnos import bp as alumnos_bp
    app.register_blueprint(alumnos_bp)
    
    from app.routes.usuarios import bp as usuarios_bp
    app.register_blueprint(usuarios_bp)
    
    # Callback para cargar usuario
    from app.models.usuario import Usuario
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Inicializar base de datos
    with app.app_context():
        db.create_all()
        
        # Crear usuario administrador por defecto si no existe
        try:
            admin_user = Usuario.query.filter_by(username='admin').first()
            if not admin_user:
                admin = Usuario(
                    rut='00.000.000-0',  # RUT especial para administrador
                    username='admin',
                    email='admin@lempar.com',
                    role='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print('[OK] Usuario administrador creado')
            else:
                print('[INFO] Usuario administrador ya existe')
        except Exception as e:
            print(f'[ERROR] Error al crear usuario admin: {e}')
            db.session.rollback()
    
    return app
