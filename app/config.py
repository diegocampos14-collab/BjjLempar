import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configuración base de la aplicación"""
    
    # Configuración de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de base de datos
    database_url = os.environ.get('DATABASE_URL')
    
    # Validar que DATABASE_URL sea una URL válida, no un hash
    if not database_url or not database_url.startswith(('sqlite://', 'postgresql://', 'postgres://')):
        print(f'[WARNING] DATABASE_URL inválida o no configurada: {database_url}')
        print('[INFO] Usando SQLite como fallback')
        # Fallback a SQLite para desarrollo local
        database_url = 'sqlite:///' + os.path.join(basedir, '..', 'alumnos.db')
    
    # Verificar si psycopg2 está disponible para PostgreSQL
    if database_url.startswith(('postgresql://', 'postgres://')):
        try:
            import psycopg2
            # Render y otras plataformas usan postgres:// pero SQLAlchemy necesita postgresql://
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
        except ImportError:
            print('[WARNING] psycopg2 no disponible, usando SQLite como fallback')
            database_url = 'sqlite:///' + os.path.join(basedir, '..', 'alumnos.db')
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    print(f'[INFO] Usando base de datos: {database_url[:50]}...')
    
    # Configuración de archivos
    UPLOAD_FOLDER = os.path.join(basedir, '..', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    
    # Crear directorio de uploads si no existe
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
