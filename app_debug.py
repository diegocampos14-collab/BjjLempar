#!/usr/bin/env python3
"""
Versión de diagnóstico mínima para identificar errores
"""
import os
import sys
from datetime import datetime, date

# Información de diagnóstico
print("=== DIAGNÓSTICO DE LA APLICACIÓN ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Environment variables:")
for key in ['DATABASE_URL', 'SECRET_KEY', 'FLASK_ENV']:
    value = os.environ.get(key, 'NOT SET')
    if key == 'DATABASE_URL' and value != 'NOT SET':
        print(f"  {key}: {value[:30]}...")
    else:
        print(f"  {key}: {value}")

try:
    from flask import Flask
    print("✅ Flask importado correctamente")
except ImportError as e:
    print(f"❌ Error importando Flask: {e}")
    sys.exit(1)

try:
    from flask_sqlalchemy import SQLAlchemy
    print("✅ Flask-SQLAlchemy importado correctamente")
except ImportError as e:
    print(f"❌ Error importando Flask-SQLAlchemy: {e}")
    sys.exit(1)

try:
    from flask_login import LoginManager
    print("✅ Flask-Login importado correctamente")
except ImportError as e:
    print(f"❌ Error importando Flask-Login: {e}")
    sys.exit(1)

# Crear aplicación mínima
app = Flask(__name__)

# Configuración básica
basedir = os.path.abspath(os.path.dirname(__file__))
database_url = os.environ.get('DATABASE_URL')

if not database_url or not database_url.startswith(('sqlite://', 'postgresql://', 'postgres://')):
    print(f'[INFO] Usando SQLite: {database_url}')
    database_url = 'sqlite:///' + os.path.join(basedir, 'debug.db')

print(f"[INFO] Database URL: {database_url}")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'debug-secret-key')

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

print("✅ Configuración básica completada")

# Modelo mínimo
class TestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

print("✅ Modelo definido")

@app.route('/')
def home():
    return """
    <h1>🎉 Aplicación Funcionando!</h1>
    <p>Si ves este mensaje, la aplicación básica está funcionando correctamente.</p>
    <p>Versión de diagnóstico - Flask App</p>
    """

@app.route('/test-db')
def test_db():
    try:
        # Crear tablas
        db.create_all()
        
        # Probar inserción
        test_record = TestModel(name='Test Record')
        db.session.add(test_record)
        db.session.commit()
        
        # Probar consulta
        records = TestModel.query.all()
        
        return f"""
        <h2>✅ Base de Datos Funcionando</h2>
        <p>Registros en la base de datos: {len(records)}</p>
        <p>Database URL: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...</p>
        """
    except Exception as e:
        return f"""
        <h2>❌ Error en Base de Datos</h2>
        <p>Error: {str(e)}</p>
        <p>Tipo: {type(e).__name__}</p>
        """

if __name__ == '__main__':
    print("=== INICIANDO APLICACIÓN DE DIAGNÓSTICO ===")
    with app.app_context():
        try:
            db.create_all()
            print("✅ Base de datos inicializada")
        except Exception as e:
            print(f"❌ Error inicializando base de datos: {e}")
    
    print("✅ Aplicación lista")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
