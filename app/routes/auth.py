from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app import db
from app.models.usuario import Usuario
from app.models.alumno import Alumno
from app.forms.auth import LoginForm, RegistroForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(username=form.username.data).first()
        if usuario and usuario.check_password(form.password.data) and usuario.is_active:
            login_user(usuario)
            flash(f'Bienvenido, {usuario.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
    
    return render_template('login.html', form=form)

@bp.route('/logout')
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro público de usuarios"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistroForm()
    if form.validate_on_submit():
        print(f'[DEBUG] Intentando registrar: {form.username.data} - {form.email.data}')
        
        # Verificar si el RUT existe en la tabla de alumnos
        alumno_existente = Alumno.query.filter_by(rut=form.rut.data).first()
        if not alumno_existente:
            flash('El RUT ingresado no corresponde a ningún alumno registrado. Contacta al administrador.', 'error')
            return render_template('registro.html', form=form)
        
        # Verificar si ya existe un usuario con este RUT
        usuario_existente = Usuario.query.filter_by(rut=form.rut.data).first()
        if usuario_existente:
            flash('Ya existe un usuario registrado con este RUT.', 'error')
            return render_template('registro.html', form=form)
        
        # Verificar si el username ya existe
        username_existente = Usuario.query.filter_by(username=form.username.data).first()
        if username_existente:
            flash('El nombre de usuario ya está en uso.', 'error')
            return render_template('registro.html', form=form)
        
        # Verificar si el email ya existe
        email_existente = Usuario.query.filter_by(email=form.email.data).first()
        if email_existente:
            flash('El email ya está registrado.', 'error')
            return render_template('registro.html', form=form)
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            rut=form.rut.data,
            username=form.username.data,
            email=form.email.data,
            role='visualizador'  # Los usuarios públicos son visualizadores por defecto
        )
        nuevo_usuario.set_password(form.password.data)
        
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash(f'Registro exitoso. Bienvenido, {nuevo_usuario.username}!', 'success')
            login_user(nuevo_usuario)  # Iniciar sesión automáticamente
            return redirect(url_for('main.home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'error')
    
    return render_template('registro.html', form=form)
