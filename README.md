# Sistema de Gestión de Alumnos de Artes Marciales - Flask

Aplicación web completa para escuelas de artes marciales, construida con Flask, SQLAlchemy y soporte para SQLite/PostgreSQL. Permite gestionar información de alumnos incluyendo cinturones, edad calculada automáticamente y seguimiento del progreso.

## Características

- **CRUD completo** de alumnos (Crear, Leer, Actualizar, Eliminar)
- **Autenticación y autorización** con roles (Admin/Visualizador)
- **Registro restringido** solo para alumnos registrados
- **Base de datos flexible** (SQLite para desarrollo, PostgreSQL para producción)
- **Validación de RUT chileno** con formato y unicidad
- **API REST** con endpoints JSON
- **Diseño responsivo** con Bootstrap 5
- **Validación de formularios** del lado cliente y servidor
- **Mensajes flash** para feedback del usuario
- **Plantillas Jinja2** reutilizables
- **Iconos Font Awesome**
- **Navegación intuitiva** con dropdown
- **Estilos CSS personalizados** con animaciones

## Instalación

1. **Crear y activar el entorno virtual:**
   ```bash
   # Crear entorno virtual
   python -m venv venv
   
   # Activar en Windows (Command Prompt)
   venv\Scripts\activate
   
   # Activar en Windows (PowerShell)
   venv\Scripts\Activate.ps1
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```

4. **Abrir en el navegador:**
   ```
   http://localhost:5000
   ```

## Estructura del Proyecto

```
sitioWeb/
├── venv/                    # Entorno virtual
├── static/
│   └── css/
│       └── style.css        # Estilos personalizados
├── templates/
│   ├── base.html            # Plantilla base
│   ├── index.html           # Página de inicio
│   ├── about.html           # Página acerca de
│   ├── alumnos.html         # Lista de alumnos
│   ├── crear_alumno.html    # Formulario crear alumno
│   ├── ver_alumno.html      # Ver detalles de alumno
│   └── editar_alumno.html   # Formulario editar alumno
├── app.py                   # Aplicación Flask principal
├── alumnos.db               # Base de datos SQLite (se crea automáticamente)
├── requirements.txt         # Dependencias
└── README.md               # Este archivo
```

## Tecnologías Utilizadas

- **Flask 3.1.1** - Framework web de Python
- **Flask-SQLAlchemy 3.1.1** - ORM para bases de datos
- **SQLite** - Base de datos ligera
- **Bootstrap 5.3.0** - Framework CSS responsivo
- **Font Awesome 6.4.0** - Iconos
- **Jinja2** - Motor de plantillas
- **HTML5 & CSS3** - Estructura y estilos
- **JavaScript** - Validación del lado cliente

## Funcionalidades

### Gestión de Alumnos
- **Crear alumno**: Formulario con validación
- **Listar alumnos**: Tabla con todos los registros
- **Ver alumno**: Detalles completos de un alumno
- **Editar alumno**: Modificar información existente
- **Eliminar alumno**: Borrar registro con confirmación

### API REST
- `GET /api/alumnos` - Obtener todos los alumnos en JSON
- `GET /api/alumno/<id>` - Obtener un alumno específico

### Rutas Web
- `/` - Página de inicio
- `/alumnos` - Lista de alumnos
- `/crear-alumno` - Formulario para crear alumno
- `/alumno/<id>` - Ver detalles de alumno
- `/editar-alumno/<id>` - Formulario para editar
- `/about` - Información del proyecto

## Desarrollo

Para agregar nuevas funcionalidades:

1. **Nuevos modelos**: Definir en `app.py` usando SQLAlchemy
2. **Nuevas rutas**: Agregar funciones con decorador `@app.route`
3. **Nuevas plantillas**: Crear en `templates/` extendiendo `base.html`
4. **Migraciones**: Usar `db.create_all()` para cambios en la BD

## Licencia

Este proyecto está bajo la Licencia MIT.
