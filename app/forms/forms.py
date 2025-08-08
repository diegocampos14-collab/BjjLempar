from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class UsuarioForm(FlaskForm):
    """Formulario para crear usuarios (solo admin)"""
    rut = StringField('RUT', validators=[DataRequired(), Length(min=9, max=12)], 
                      render_kw={'placeholder': '12.345.678-9', 'pattern': r'[0-9]{1,2}\.[0-9]{3}\.[0-9]{3}-[0-9kK]{1}'})
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Rol', choices=[('admin', 'Administrador'), ('visualizador', 'Visualizador')], validators=[DataRequired()])
    submit = SubmitField('Crear Usuario')
