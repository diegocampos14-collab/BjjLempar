from datetime import datetime, date
from app import db

class Alumno(db.Model):
    """Modelo de Alumno para gestión de estudiantes de artes marciales"""
    
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
        """Convierte el objeto a diccionario para JSON"""
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
