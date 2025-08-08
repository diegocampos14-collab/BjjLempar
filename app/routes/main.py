from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.models.alumno import Alumno

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    """Página principal"""
    return render_template('home.html')

@bp.route('/api/alumnos', methods=['GET'])
@login_required
def api_alumnos():
    """API endpoint para obtener todos los alumnos"""
    alumnos = Alumno.query.all()
    return jsonify([alumno.to_dict() for alumno in alumnos])

@bp.route('/init-db')
def init_db():
    """Inicializar base de datos y crear usuario admin"""
    from app import db
    from app.models.usuario import Usuario
    
    try:
        # Crear todas las tablas
        db.create_all()
        
        # Crear usuario administrador por defecto si no existe
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
            
            return '''
            <h2>✅ Base de Datos Inicializada</h2>
            <p>Usuario administrador creado exitosamente:</p>
            <ul>
                <li><strong>Usuario:</strong> admin</li>
                <li><strong>Contraseña:</strong> admin123</li>
                <li><strong>Rol:</strong> Administrador</li>
            </ul>
            <p><a href="/login">Ir al Login</a></p>
            <p><strong>ADVERTENCIA:</strong> Cambia la contraseña en producción</p>
            '''
        else:
            return '''
            <h2>ℹ️ Base de Datos Ya Inicializada</h2>
            <p>El usuario administrador ya existe.</p>
            <p><a href="/login">Ir al Login</a></p>
            '''
    except Exception as e:
        db.session.rollback()
        return f'''
        <h2>❌ Error al Inicializar</h2>
        <p>Error: {str(e)}</p>
        <p><a href="/">Volver al inicio</a></p>
        '''
