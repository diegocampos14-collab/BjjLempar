#!/usr/bin/env python3
"""
Aplicación Flask ultra-mínima para verificar que Render funciona
"""
import os
from flask import Flask

# Crear aplicación Flask básica
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema Alumnos - Funcionando</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .success { color: #28a745; }
            .info { color: #17a2b8; background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="success">🎉 ¡Aplicación Funcionando! v2</h1>
            <p>Tu aplicación Flask está desplegada correctamente en Render.</p>
            
            <div class="info">
                <h3>📋 Estado del Sistema:</h3>
                <ul>
                    <li>✅ Flask funcionando</li>
                    <li>✅ Render deployment exitoso</li>
                    <li>✅ Python ejecutándose correctamente</li>
                    <li>✅ Servidor web activo</li>
                </ul>
            </div>
            
            <h3>🔧 Información Técnica:</h3>
            <p><strong>Puerto:</strong> {}</p>
            <p><strong>Entorno:</strong> {}</p>
            
            <h3>🚀 Próximos Pasos:</h3>
            <p>Una vez confirmado que esta versión funciona, podemos restaurar la aplicación completa paso a paso.</p>
        </div>
    </body>
    </html>
    """.format(
        os.environ.get('PORT', '5000'),
        os.environ.get('FLASK_ENV', 'development')
    )

@app.route('/health')
def health():
    return {
        'status': 'OK',
        'message': 'Aplicación funcionando correctamente',
        'port': os.environ.get('PORT', '5000'),
        'env': os.environ.get('FLASK_ENV', 'development')
    }

@app.route('/test')
def test():
    return """
    <h2>🧪 Página de Prueba</h2>
    <p>Esta es una página de prueba adicional.</p>
    <p><a href="/">← Volver al inicio</a></p>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
