from flask import Blueprint, render_template, request
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/habitaciones')
def mostrar_habitaciones():
    entrada = request.args.get('entrada')  # Fecha de entrada
    salida = request.args.get('salida')  # Fecha de salida
    
    # Aquí simulas la disponibilidad de habitaciones (esto se puede expandir)
    habitaciones = [
        {"id": 1, "tipo": "Estándar", "precio": 100, "disponibilidad": True},
        {"id": 2, "tipo": "Suite", "precio": 200, "disponibilidad": False},
    ]

    # Puedes pasar las fechas a la plantilla para visualizarlas o usarlas para filtrado
    return render_template('habitaciones.html', habitaciones=habitaciones, entrada=entrada, salida=salida)


