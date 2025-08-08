from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.usuario import Usuario
from app.forms.forms import UsuarioForm
from app.utils.decorators import admin_required

bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@bp.route('/')
@login_required
@admin_required
def listar_usuarios():
    """Lista todos los usuarios (solo admin)"""
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@bp.route('/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_usuario():
    """Crear un nuevo usuario (solo admin)"""
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
        
        # Verificar si el RUT ya existe
        existing_rut = Usuario.query.filter_by(rut=form.rut.data).first()
        if existing_rut:
            flash('El RUT ya está registrado.', 'error')
            return render_template('crear_usuario.html', form=form)
        
        # Crear nuevo usuario
        usuario = Usuario(
            rut=form.rut.data,
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        usuario.set_password(form.password.data)
        
        try:
            db.session.add(usuario)
            db.session.commit()
            flash(f'Usuario {usuario.username} creado exitosamente.', 'success')
            return redirect(url_for('usuarios.listar_usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'error')
    
    return render_template('crear_usuario.html', form=form)

@bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_usuario(id):
    """Eliminar un usuario (solo admin)"""
    try:
        usuario = Usuario.query.get_or_404(id)
        
        # No permitir que un usuario se elimine a sí mismo
        if usuario.id == current_user.id:
            flash('No puedes eliminar tu propia cuenta.', 'error')
            return redirect(url_for('usuarios.listar_usuarios'))
        
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuario {usuario.username} eliminado exitosamente.', 'success')
    except Exception as e:
        flash(f'Error al eliminar usuario: {str(e)}', 'error')
    
    return redirect(url_for('usuarios.listar_usuarios'))

@bp.route('/debug')
def debug_usuarios():
    """Ruta temporal para debug - ver todos los usuarios"""
    usuarios = Usuario.query.all()
    debug_info = []
    for user in usuarios:
        debug_info.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'rut': user.rut,
            'role': user.role,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else 'N/A'
        })
    
    from flask import jsonify
    return jsonify(debug_info)
