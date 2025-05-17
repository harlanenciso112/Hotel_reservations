from flask import Flask
from flask_mail import Mail
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

mail = Mail()

def create_app():
    app = Flask(__name__, static_folder='static')
    
    # Configuración de la aplicación
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    
    # Configuración de correo
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Inicializar extensiones
    mail.init_app(app)
    
    # Registro de blueprints
    from .routes import main
    app.register_blueprint(main)
    
    return app
