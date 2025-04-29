from flask import Blueprint, render_template, request
from datetime import datetime

main = Blueprint('main', __name__)

habitaciones = [
    {"id": 1, "tipo": "Habitación Individual", "precio": 100, "disponibilidad": True},
    {"id": 2, "tipo": "Habitación Doble", "precio": 150, "disponibilidad": False},
    {"id": 3, "tipo": "Suite", "precio": 250, "disponibilidad": True},
]

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/habitaciones')
def habitaciones_page():
    inicio = request.args.get('inicio')
    fin = request.args.get('fin')
    
    if inicio and fin:
        inicio_fecha = datetime.strptime(inicio, '%Y-%m-%d')
        fin_fecha = datetime.strptime(fin, '%Y-%m-%d')
        
        habitaciones_disponibles = [h for h in habitaciones if h["disponibilidad"]]
        
        return render_template('habitaciones.html', habitaciones=habitaciones_disponibles, inicio=inicio_fecha, fin=fin_fecha)
    else:
        return render_template('habitaciones.html', habitaciones=[], mensaje="No se han seleccionado fechas válidas.")

