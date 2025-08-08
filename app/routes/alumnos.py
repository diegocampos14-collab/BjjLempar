from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from app import db
from app.models.alumno import Alumno
from app.utils.decorators import admin_required
from app.utils.helpers import save_picture, delete_picture

bp = Blueprint('alumnos', __name__, url_prefix='/alumnos')

@bp.route('/')
@login_required
def listar_alumnos():
    """Lista todos los alumnos"""
    alumnos = Alumno.query.all()
    return render_template('alumnos.html', alumnos=alumnos)

@bp.route('/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_alumno():
    """Crear un nuevo alumno"""
    if request.method == 'POST':
        try:
            rut = request.form['rut']
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            fecha_nacimiento_str = request.form['fecha_nacimiento']
            cinturon = request.form['cinturon']
            nivel = int(request.form['nivel'])
            
            # Verificar si el RUT ya existe
            existing_alumno = Alumno.query.filter_by(rut=rut).first()
            if existing_alumno:
                flash('Ya existe un alumno con este RUT', 'error')
                return render_template('crear_alumno.html')
            
            # Convertir fecha de string a date
            fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
            
            # Manejar foto si se subió
            foto_filename = None
            if 'foto' in request.files:
                foto = request.files['foto']
                if foto and foto.filename != '':
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
            return redirect(url_for('alumnos.listar_alumnos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear alumno: {str(e)}', 'error')
            return render_template('crear_alumno.html')
    
    return render_template('crear_alumno.html')

@bp.route('/<int:id>')
@login_required
def ver_alumno(id):
    """Ver detalles de un alumno"""
    alumno = Alumno.query.get_or_404(id)
    return render_template('ver_alumno.html', alumno=alumno)

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_alumno(id):
    """Editar un alumno existente"""
    alumno = Alumno.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            nuevo_rut = request.form['rut']
            
            # Verificar si el RUT ya existe en otro alumno
            if nuevo_rut != alumno.rut:  # Solo verificar si el RUT cambió
                existing_alumno = Alumno.query.filter_by(rut=nuevo_rut).first()
                if existing_alumno:
                    flash('Ya existe otro alumno con este RUT', 'error')
                    return render_template('editar_alumno.html', alumno=alumno)
            
            # Actualizar datos
            alumno.rut = nuevo_rut
            alumno.nombre = request.form['nombre']
            alumno.apellido = request.form['apellido']
            alumno.fecha_nacimiento = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date()
            alumno.cinturon = request.form['cinturon']
            alumno.nivel = int(request.form['nivel'])
            
            # Manejar foto si se subió una nueva
            if 'foto' in request.files:
                foto = request.files['foto']
                if foto and foto.filename != '':
                    # Eliminar foto anterior si existe
                    if alumno.foto:
                        delete_picture(alumno.foto)
                    # Guardar nueva foto
                    alumno.foto = save_picture(foto)
            
            db.session.commit()
            flash('Alumno actualizado exitosamente', 'success')
            return redirect(url_for('alumnos.ver_alumno', id=alumno.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar alumno: {str(e)}', 'error')
    
    return render_template('editar_alumno.html', alumno=alumno)

@bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_alumno(id):
    """Eliminar un alumno"""
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
    
    return redirect(url_for('alumnos.listar_alumnos'))
