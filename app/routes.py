from flask import Blueprint, render_template, request
from datetime import datetime
from .db import obtener_conexion

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/habitaciones')
def mostrar_habitaciones():
    entrada = request.args.get('entrada')  
    salida = request.args.get('salida')
    
    # Obtener los filtros (ahora pueden ser listas para múltiples selecciones)
    tipos = request.args.getlist('tipo')
    camas = request.args.getlist('camas')
    precios = request.args.getlist('precio')
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Construir la consulta base - solo habitaciones disponibles
    query = "SELECT * FROM habitaciones WHERE disponibilidad = True"
    filtros = []
    
    # Aplicar filtros de tipo si existen
    if tipos:
        placeholders = ', '.join(['%s'] * len(tipos))
        query += f" AND tipo IN ({placeholders})"
        filtros.extend(tipos)
    
    # Aplicar filtros de camas si existen
    if camas:
        placeholders = ', '.join(['%s'] * len(camas))
        query += f" AND camas IN ({placeholders})"
        filtros.extend([int(c) for c in camas])
    
    # Aplicar filtros de precio si existen
    if precios:
        # Ordenar precios de mayor a menor para aplicar el menor precio máximo
        precio_max = min([float(p) for p in precios])
        query += " AND precio <= %s"
        filtros.append(precio_max)
    
    # Ejecutar la consulta
    cursor.execute(query, filtros)
    habitaciones = cursor.fetchall()
    
    # Asegurar que todas las habitaciones tengan los campos necesarios
    for hab in habitaciones:
        # Si no existe el campo metros, añadirlo
        if 'metros' not in hab:
            hab['metros'] = 20 + (10 * (int(hab.get('camas', 1)) - 1))
    
    cursor.close()
    conn.close()
    
    return render_template('habitaciones.html', habitaciones=habitaciones, entrada=entrada, salida=salida)

@main.route('/reservas')
def mostrar_reservas():
    # Obteniendo datos de la habitación seleccionada
    id_habitacion = request.args.get('id_habitacion')
    tipo = request.args.get('tipo')
    camas = request.args.get('camas')
    precio = request.args.get('precio')
    entrada = request.args.get('entrada')
    salida = request.args.get('salida')
    
    # Calcular número de días
    dias = 0
    if entrada and salida:
        fecha_entrada = datetime.strptime(entrada, '%Y-%m-%d')
        fecha_salida = datetime.strptime(salida, '%Y-%m-%d')
        dias = (fecha_salida - fecha_entrada).days
    
    # Aquí podrías obtener más detalles de la habitación desde la base de datos si es necesario
    
    return render_template('reservas.html', 
                          id_habitacion=id_habitacion,
                          tipo=tipo,
                          camas=camas,
                          precio=precio,
                          entrada=entrada, 
                          salida=salida,
                          dias=dias)

@main.route('/procesar_reserva', methods=['POST'])
def procesar_reserva():
    if request.method == 'POST':
        # Obtener los datos del formulario
        id_habitacion = request.form.get('id_habitacion')
        entrada = request.form.get('entrada')
        salida = request.form.get('salida')
        precio_total = request.form.get('precio_total')
        
        # Datos del cliente
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        documento = request.form.get('documento')
        huespedes = request.form.get('huespedes')
        comentarios = request.form.get('comentarios', '')
        metodo_pago = request.form.get('metodo_pago')
        
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            
            # 1. Guardar datos del cliente (si no existe)
            cursor.execute(
                "INSERT INTO clientes (nombre, email, telefono, documento) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE nombre=%s",
                (nombre, email, telefono, documento, nombre)
            )
            
            # Obtener el ID del cliente (ya sea el recién insertado o el existente)
            cursor.execute("SELECT id FROM clientes WHERE documento = %s", (documento,))
            resultado = cursor.fetchone()
            cliente_id = resultado['id']  # Accede al valor por nombre de columna
            
            # 2. Crear la reserva
            fecha_reserva = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                """INSERT INTO reservas 
                (cliente_id, habitacion_id, fecha_reserva, fecha_entrada, fecha_salida, 
                num_huespedes, precio_total, metodo_pago, comentarios, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'confirmada')""",
                (cliente_id, id_habitacion, fecha_reserva, entrada, 
                 salida, huespedes, precio_total, metodo_pago, comentarios)
            )
            
            # Obtener el ID de la reserva recién creada
            reserva_id = cursor.lastrowid
            
            # 3. Actualizar estado de la habitación a ocupada
            cursor.execute(
                "UPDATE habitaciones SET disponibilidad = FALSE WHERE id = %s",
                (id_habitacion,)
            )
            
            # Confirmar los cambios en la base de datos
            conn.commit()
            
            # Redirigir a una página de confirmación
            return render_template('confirmacion.html', 
                                  reserva_id=reserva_id,
                                  nombre=nombre,
                                  entrada=entrada,
                                  salida=salida)
            
        except Exception as e:
            # Si hay un error, hacer rollback y mostrar error
            conn.rollback()
            return render_template('error.html', error=str(e))
        
        finally:
            # Cerrar conexión
            cursor.close()
            conn.close()