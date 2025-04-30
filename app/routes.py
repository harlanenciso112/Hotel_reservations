from flask import Blueprint, render_template, request
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/habitaciones')
def mostrar_habitaciones():
    entrada = request.args.get('entrada')  
    salida = request.args.get('salida')  
    
    habitaciones = [
        {"id": 1, "tipo": "Estándar", "precio": 100, "disponibilidad": True},
        {"id": 2, "tipo": "Suite", "precio": 200, "disponibilidad": False},
        {"id": 3, "tipo": "Suite", "precio": 201, "disponibilidad": False},
        {"id": 1, "tipo": "Estándar", "precio": 100, "disponibilidad": True},
        {"id": 2, "tipo": "Suite", "precio": 200, "disponibilidad": False},
        {"id": 3, "tipo": "Suite", "precio": 201, "disponibilidad": False},
    ]
    
    return render_template('habitaciones.html', habitaciones=habitaciones, entrada=entrada, salida=salida)


