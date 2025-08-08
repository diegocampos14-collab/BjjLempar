#!/usr/bin/env python3
"""
Punto de entrada principal para la aplicación Flask
Sistema de Gestión de Alumnos de Artes Marciales - Lempar
"""

import os
from app import create_app
from app.config import config

# Determinar el entorno
config_name = os.environ.get('FLASK_ENV', 'default')
app = create_app(config[config_name])

if __name__ == '__main__':
    # Para desarrollo local
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
else:
    # Para producción (Render, Heroku, etc.)
    print('[INFO] Aplicación iniciada en modo producción')
    print(f'[INFO] Configuración: {config_name}')
    print('[INFO] Sistema de Gestión de Alumnos - Lempar')
