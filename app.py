from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid
from functools import wraps
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))

# Configuración flexible de base de datos
database_url = os.environ.get('DATABASE_URL')

# Validar que DATABASE_URL sea una URL válida, no un hash
if not database_url or not database_url.startswith(('sqlite://', 'postgresql://', 'postgres://')):
    print(f'[WARNING] DATABASE_URL inválida o no configurada: {database_url}')
    print('[INFO] Usando SQLite como fallback')
    # Fallback a SQLite para desarrollo local
    database_url = 'sqlite:///' + os.path.join(basedir, 'alumnos.db')

# Render y otras plataformas usan postgres:// pero SQLAlchemy necesita postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

print(f'[INFO] Usando base de datos: {database_url[:50]}...')

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu-clave-secreta-para-desarrollo')

# Configuración para subida de archivos
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Crear directorio de uploads si no existe
if not os.path.exists(UPLOAD_FOLDER): # si no existe el directorio de uploads
    os.makedirs(UPLOAD_FOLDER)

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Funciones auxiliares para manejo de archivos
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_picture(form_picture):
    if form_picture and allowed_file(form_picture.filename):
        # Generar nombre único para el archivo
        random_hex = uuid.uuid4().hex
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_fn)
        
        # Guardar el archivo
        form_picture.save(picture_path)
        return picture_fn
    return None

def delete_picture(picture_filename):
    if picture_filename:
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_filename)
        if os.path.exists(picture_path):
            os.remove(picture_path)

# Modelo de Alumno
class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(12), unique=True, nullable=False)  # RUT chileno formato XX.XXX.XXX-X
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    cinturon = db.Column(db.String(50), nullable=False)
    nivel = db.Column(db.Integer, nullable=False)  # Rayitas del 1 al 4
    foto = db.Column(db.String(200), nullable=True)  # Ruta de la foto
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Alumno {self.nombre} {self.apellido} - {self.cinturon} {self.nivel} rayitas>'
    
    @property
    def edad(self):
        """Calcula la edad basada en la fecha de nacimiento"""
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
    
    @property
    def cinturon_completo(self):
        """Retorna el cinturón con el nivel de rayitas"""
        if self.nivel == 0:
            return f"{self.cinturon} - Sin rayitas"
        elif self.nivel == 1:
            return f"{self.cinturon} - {self.nivel} rayita"
        else:
            return f"{self.cinturon} - {self.nivel} rayitas"
    
    def to_dict(self):
        return {
            'id': self.id,
            'rut': self.rut,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'fecha_nacimiento': self.fecha_nacimiento.strftime('%Y-%m-%d'),
            'cinturon': self.cinturon,
            'nivel': self.nivel,
            'cinturon_completo': self.cinturon_completo,
            'foto': self.foto,
            'edad': self.edad,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')
        }

# Modelo de Usuario
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(12), unique=True, nullable=False)  # RUT del alumno asociado
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='visualizador')  # 'admin' o 'visualizador'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Usuario {self.username} - {self.role}>'
    
    def set_password(self, password):
        """Genera hash de la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.role == 'admin'
    
    def is_visualizador(self):
        """Verifica si el usuario es visualizador"""
        return self.role == 'visualizador'

# Callback para cargar usuario
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Decorador para requerir rol admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Formularios
class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class RegistroForm(FlaskForm):
    rut = StringField('RUT', validators=[DataRequired(), Length(min=9, max=12)], 
                      render_kw={'placeholder': '12.345.678-9', 'pattern': '[0-9]{1,2}\.[0-9]{3}\.[0-9]{3}-[0-9kK]{1}'})
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Registrarse')

class UsuarioForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Rol', choices=[('admin', 'Administrador'), ('visualizador', 'Visualizador')], validators=[DataRequired()])
    submit = SubmitField('Crear Usuario')

@app.route('/')
@login_required
def home():
    return render_template('index.html')

# Rutas de Autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(username=form.username.data).first()
        if usuario and usuario.check_password(form.password.data) and usuario.is_active:
            login_user(usuario)
            flash(f'Bienvenido, {usuario.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistroForm()
    if form.validate_on_submit():
        print(f'[DEBUG] Intentando registrar: {form.username.data} - {form.email.data}')
        
        # Verificar si el RUT existe en la tabla de alumnos
        alumno_existente = Alumno.query.filter_by(rut=form.rut.data).first()
        if not alumno_existente:
            flash('Para registrarte en la aplicación debes ser un alumno de la academia. El RUT ingresado no está registrado como alumno.', 'error')
            return render_template('registro.html', form=form)
        
        # Verificar si ya existe un usuario con este RUT
        usuario_con_rut = Usuario.query.filter_by(rut=form.rut.data).first()
        if usuario_con_rut:
            flash(f'Ya existe un usuario registrado con el RUT {form.rut.data}. Usuario: {usuario_con_rut.username}', 'error')
            return render_template('registro.html', form=form)
        
        # Verificar si el usuario ya existe
        existing_user = Usuario.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('El nombre de usuario ya existe. Elige otro.', 'error')
            return render_template('registro.html', form=form)
        
        # Verificar si el email ya existe
        existing_email = Usuario.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash(f'El email {form.email.data} ya está registrado por el usuario: {existing_email.username}. Usa otro email.', 'error')
            return render_template('registro.html', form=form)
        
        # Crear nuevo usuario con rol de visualizador
        nuevo_usuario = Usuario(
            rut=form.rut.data,
            username=form.username.data,
            email=form.email.data,
            role='visualizador'  # Todos los registros públicos son visualizadores
        )
        nuevo_usuario.set_password(form.password.data)
        
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash(f'Registro exitoso. Bienvenido, {nuevo_usuario.username}!', 'success')
            login_user(nuevo_usuario)  # Iniciar sesión automáticamente
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'error')
    
    return render_template('registro.html', form=form)

@app.route('/debug-usuarios')
def debug_usuarios():
    """Ruta temporal para debug - ver todos los usuarios"""
    usuarios = Usuario.query.all()
    debug_info = []
    for user in usuarios:
        debug_info.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at
        })
    return jsonify(debug_info)

@app.route('/usuarios')
@login_required
@admin_required
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/crear-usuario', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_usuario():
    form = UsuarioForm()
    if form.validate_on_submit():
        # Verificar si el usuario ya existe
        existing_user = Usuario.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('El nombre de usuario ya existe.', 'error')
            return render_template('crear_usuario.html', form=form)
        
        # Verificar si el email ya existe
        existing_email = Usuario.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('El email ya está registrado.', 'error')
            return render_template('crear_usuario.html', form=form)
        
        # Crear nuevo usuario
        usuario = Usuario(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        usuario.set_password(form.password.data)
        
        db.session.add(usuario)
        db.session.commit()
        
        flash(f'Usuario {usuario.username} creado exitosamente.', 'success')
        return redirect(url_for('listar_usuarios'))
    
    return render_template('crear_usuario.html', form=form)

@app.route('/eliminar-usuario/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_usuario(id):
    try:
        usuario = Usuario.query.get_or_404(id)
        
        # No permitir que un usuario se elimine a sí mismo
        if usuario.id == current_user.id:
            flash('No puedes eliminar tu propia cuenta.', 'error')
            return redirect(url_for('listar_usuarios'))
        
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuario {usuario.username} eliminado exitosamente.', 'success')
    except Exception as e:
        flash(f'Error al eliminar usuario: {str(e)}', 'error')
    
    return redirect(url_for('listar_usuarios'))

@app.route('/alumnos')
@login_required
def listar_alumnos():
    alumnos = Alumno.query.all()
    return render_template('alumnos.html', alumnos=alumnos)

@app.route('/crear-alumno', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_alumno():
    if request.method == 'POST':
        try:
            from datetime import datetime
            
            rut = request.form['rut']
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            fecha_nacimiento_str = request.form['fecha_nacimiento']
            cinturon = request.form['cinturon']
            nivel = int(request.form['nivel'])
            
            # Verificar si el RUT ya existe
            existing_alumno = Alumno.query.filter_by(rut=rut).first()
            if existing_alumno:
                flash(f'Ya existe un alumno registrado con el RUT {rut}. Alumno: {existing_alumno.nombre} {existing_alumno.apellido}', 'error')
                return render_template('crear_alumno.html')
            
            # Convertir string de fecha a objeto date
            fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
            
            # Manejar la foto
            foto_filename = None
            if 'foto' in request.files:
                foto = request.files['foto']
                if foto.filename != '':
                    foto_filename = save_picture(foto)
            
            # Crear nuevo alumno
            nuevo_alumno = Alumno(
                rut=rut,
                nombre=nombre,
                apellido=apellido,
                fecha_nacimiento=fecha_nacimiento,
                cinturon=cinturon,
                nivel=nivel,
                foto=foto_filename
            )
            
            db.session.add(nuevo_alumno)
            db.session.commit()
            
            flash('Alumno creado exitosamente', 'success')
            return redirect(url_for('listar_alumnos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear alumno: {str(e)}', 'error')
            return render_template('crear_alumno.html')
    
    return render_template('crear_alumno.html')

@app.route('/alumno/<int:id>')
@login_required
def ver_alumno(id):
    alumno = Alumno.query.get_or_404(id)
    return render_template('ver_alumno.html', alumno=alumno)

@app.route('/editar-alumno/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_alumno(id):
    alumno = Alumno.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            from datetime import datetime
            
            nuevo_rut = request.form['rut']
            
            # Verificar si el RUT ya existe en otro alumno
            if nuevo_rut != alumno.rut:  # Solo verificar si el RUT cambió
                existing_alumno = Alumno.query.filter_by(rut=nuevo_rut).first()
                if existing_alumno:
                    flash(f'Ya existe un alumno registrado con el RUT {nuevo_rut}. Alumno: {existing_alumno.nombre} {existing_alumno.apellido}', 'error')
                    return render_template('editar_alumno.html', alumno=alumno)
            
            alumno.rut = nuevo_rut
            alumno.nombre = request.form['nombre']
            alumno.apellido = request.form['apellido']
            fecha_nacimiento_str = request.form['fecha_nacimiento']
            alumno.cinturon = request.form['cinturon']
            alumno.nivel = int(request.form['nivel'])
            
            # Convertir string de fecha a objeto date
            alumno.fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
            
            # Manejar la foto
            if 'foto' in request.files:
                foto = request.files['foto']
                if foto.filename != '':
                    # Eliminar foto anterior si existe
                    if alumno.foto:
                        delete_picture(alumno.foto)
                    # Guardar nueva foto
                    alumno.foto = save_picture(foto)
            
            db.session.commit()
            flash('Alumno actualizado exitosamente', 'success')
            return redirect(url_for('ver_alumno', id=alumno.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar alumno: {str(e)}', 'error')
    
    return render_template('editar_alumno.html', alumno=alumno)

@app.route('/eliminar-alumno/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_alumno(id):
    try:
        alumno = Alumno.query.get_or_404(id)
        
        # Eliminar foto si existe
        if alumno.foto:
            delete_picture(alumno.foto)
        
        db.session.delete(alumno)
        db.session.commit()
        flash('Alumno eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar alumno: {str(e)}', 'error')
    
    return redirect(url_for('listar_alumnos'))

# API endpoints
@app.route('/api/alumnos', methods=['GET'])
def api_alumnos():
    alumnos = Alumno.query.all()
    return jsonify([alumno.to_dict() for alumno in alumnos])

@app.route('/api/alumno/<int:id>', methods=['GET'])
def api_alumno(id):
    alumno = Alumno.query.get_or_404(id)
    return jsonify(alumno.to_dict())

@app.route('/about')
def about():
    return render_template('about.html')

# @app.route('/fix-admin-rut')
# def fix_admin_rut():
#     """Ruta temporal para corregir el RUT del admin"""
#     admin_user = Usuario.query.filter_by(username='admin').first()
#     if admin_user:
#         old_rut = admin_user.rut
#         admin_user.rut = '00.000.000-0'  # RUT especial para admin
#         db.session.commit()
#         return f'RUT del admin actualizado de {old_rut} a {admin_user.rut}'
#     return 'Usuario admin no encontrado'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Crear usuario administrador por defecto si no existe
        try:
            admin_user = Usuario.query.filter_by(username='admin').first()
            if not admin_user:
                admin = Usuario(
                    rut='00.000.000-0',  # RUT especial para administrador (no válido para alumnos)
                    username='admin',
                    email='admin@lempar.com',
                    role='admin'
                )
                admin.set_password('admin123')  # Cambiar en producción
                db.session.add(admin)
                db.session.commit()
                print('[OK] Usuario administrador creado:')
                print('  Usuario: admin')
                print('  Contrasena: admin123')
                print('  [ADVERTENCIA] Cambia la contrasena en produccion')
            else:
                print('[INFO] Usuario administrador ya existe')
        except Exception as e:
            print(f'[ERROR] Error al crear usuario admin: {e}')
            db.session.rollback()
        
        # Crear alumnos de prueba si no existen (comentado para evitar errores en producción)
        # if Alumno.query.count() == 0:
        #     from datetime import date
        #     alumnos_prueba = [
        #         {
        #             'rut': '12.345.678-9',
        #             'nombre': 'Juan',
        #             'apellido': 'Pérez',
        #             'fecha_nacimiento': date(1995, 5, 15),
        #             'cinturon': 'Azul',
        #             'nivel': 2
        #         }
        #     ]
        #     
        #     for alumno_data in alumnos_prueba:
        #         alumno = Alumno(**alumno_data)
        #         db.session.add(alumno)
        #     
        #     db.session.commit()
        #     print('[OK] Alumnos de prueba creados.')
        
        # Mostrar información de usuarios existentes
        usuarios_existentes = Usuario.query.all()
        print(f'[DEBUG] Usuarios en la base de datos: {len(usuarios_existentes)}')
        for user in usuarios_existentes:
            print(f'  - {user.username} ({user.email}) - {user.role} - RUT: {user.rut}')
        
        # Mostrar alumnos existentes
        alumnos_existentes = Alumno.query.all()
        print(f'[DEBUG] Alumnos en la base de datos: {len(alumnos_existentes)}')
        for alumno in alumnos_existentes:
            print(f'  - {alumno.nombre} {alumno.apellido} - RUT: {alumno.rut} - {alumno.cinturon}')
        
        print('[OK] Base de datos inicializada correctamente.')
    
    app.run(debug=True)
