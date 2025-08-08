import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename

def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_picture(form_picture):
    """Guarda una imagen subida y retorna el nombre del archivo"""
    if form_picture and allowed_file(form_picture.filename):
        # Generar nombre único para evitar colisiones
        random_hex = uuid.uuid4().hex
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_filename = random_hex + f_ext
        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_filename)
        
        # Guardar archivo
        form_picture.save(picture_path)
        return picture_filename
    return None

def delete_picture(picture_filename):
    """Elimina una imagen del sistema de archivos"""
    if picture_filename:
        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_filename)
        if os.path.exists(picture_path):
            os.remove(picture_path)
