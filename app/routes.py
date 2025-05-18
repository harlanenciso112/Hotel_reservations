from flask import Blueprint, render_template, request, url_for
from datetime import datetime
from .db import obtener_conexion
import random
import string
import os
from .emails import send_reservation_confirmation  # Importa la función


main = Blueprint('main', __name__)
MERCADOPAGO_PUBLIC_KEY = os.getenv("MERCADOPAGO_PUBLIC_KEY")
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
                          dias=dias,
                          mp_public_key=MERCADOPAGO_PUBLIC_KEY)

@main.route('/procesar_reserva', methods=['POST'])
def procesar_reserva():
    if request.method == 'POST':
        # Obtener datos del formulario
        id_habitacion = request.form.get('id_habitacion')
        entrada = request.form.get('entrada')
        salida = request.form.get('salida')
        precio_total = request.form.get('precio_total')
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        documento = request.form.get('documento', '')
        huespedes = request.form.get('huespedes', '1')
        comentarios = request.form.get('comentarios', '')
        
        # Información de pago
        payment_id = request.form.get('payment_id', '')
        metodo_pago = request.form.get('metodo_pago', 'No especificado')
        
        # Formatear el método de pago para mostrar
        metodo_formateado = "Mercado Pago"
        if metodo_pago != 'mercadopago':
            if metodo_pago == 'credit_card':
                metodo_formateado = "Tarjeta de crédito"
            elif metodo_pago == 'debit_card':
                metodo_formateado = "Tarjeta de débito"
            elif metodo_pago == 'bank_transfer':
                metodo_formateado = "Transferencia bancaria"
            elif metodo_pago == 'ticket':
                metodo_formateado = "Pago en efectivo"
            elif metodo_pago == 'wallet_purchase':
                metodo_formateado = "Billetera Mercado Pago"
            else:
                metodo_formateado = metodo_pago
        
        info_pago = f"{metodo_formateado} - ID: {payment_id}"
        
        # Generar número de reserva
        numero_reserva = "BIO" + ''.join(random.choices(string.digits, k=6))
        
        # Guardar la reserva en la base de datos
        conn = None
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            
            # Insertar la reserva en la tabla reservas
            query = """
            INSERT INTO reservas 
            (numero_reserva, id_habitacion, nombre_cliente, email, telefono, 
             fecha_entrada, fecha_salida, precio_total, metodo_pago, payment_id, 
             documento, num_huespedes, comentarios, fecha_reserva, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'confirmada')
            """
            
            # Convertir valores si es necesario
            try:
                precio_total = float(precio_total)
                huespedes = int(huespedes)
            except ValueError:
                raise ValueError("El precio total o número de huéspedes no es válido")
            
            cursor.execute(query, (
                numero_reserva,
                id_habitacion,
                nombre,
                email,
                telefono,
                entrada,
                salida,
                precio_total,
                metodo_formateado,
                payment_id,
                documento,
                huespedes,
                comentarios
            ))
            
            # Actualizar la disponibilidad de la habitación
            query_update = """
            UPDATE habitaciones 
            SET disponibilidad = False 
            WHERE id = %s
            """
            cursor.execute(query_update, (id_habitacion,))
            
            # Confirmar los cambios
            conn.commit()
            
            # Cerrar conexión
            cursor.close()
            conn.close()
            
            # Preparar datos para el correo
            reservation_data = {
                'numero_reserva': numero_reserva,
                'nombre': nombre,
                'email': email,
                'telefono': telefono,
                'documento': documento,
                'entrada': entrada,
                'salida': salida,
                'id_habitacion': id_habitacion,
                'huespedes': huespedes,
                'precio_total': precio_total,
                'metodo_pago': info_pago,
                'comentarios': comentarios
            }
            
            # Enviar correos de confirmación
            try:
                send_reservation_confirmation(reservation_data)
            except Exception as mail_error:
                print(f"Error al enviar correos: {mail_error}")
                # Continuar aunque falle el envío de correos
            
            return render_template('confirmacion.html', 
                                  numero_reserva=numero_reserva,
                                  nombre=nombre,
                                  email=email,
                                  entrada=entrada,
                                  salida=salida,
                                  metodo_pago=info_pago,
                                  precio_total=precio_total)
                                  
        except Exception as e:
            # En caso de error, hacer rollback y mostrar página de error
            if conn:
                conn.rollback()
                cursor.close()
                conn.close()
            
            print(f"Error al guardar la reserva: {e}")
            return render_template('error.html', 
                                  mensaje=f"Error al procesar la reserva: {str(e)}",
                                  volver_url=request.referrer or url_for('main.home'))
        

@main.route('/cancelar-reserva')
def cancelar_reserva():
    """Muestra la página para buscar y cancelar una reserva"""
    return render_template('cancelar_reserva.html')

@main.route('/buscar-reserva')
def buscar_reserva():
    """Busca una reserva por su número y muestra los detalles"""
    numero_reserva = request.args.get('numero_reserva', '')
    
    if not numero_reserva:
        return render_template('cancelar_reserva.html', 
                              mensaje="Por favor, ingresa un número de reserva",
                              clase_mensaje="error",
                              busqueda_realizada=False)
    
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # Buscar la reserva
        query = """
        SELECT r.*, h.tipo 
        FROM reservas r
        JOIN habitaciones h ON r.id_habitacion = h.id
        WHERE r.numero_reserva = %s
        """
        cursor.execute(query, (numero_reserva,))
        reserva = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if reserva:
            return render_template('cancelar_reserva.html', 
                                  reserva=reserva,
                                  tipo_habitacion=reserva['tipo'],
                                  busqueda_realizada=True)
        else:
            return render_template('cancelar_reserva.html', 
                                  mensaje="No se encontró ninguna reserva con ese número",
                                  clase_mensaje="error",
                                  busqueda_realizada=True)
    
    except Exception as e:
        print(f"Error al buscar reserva: {e}")
        return render_template('cancelar_reserva.html', 
                              mensaje=f"Error al buscar la reserva: {str(e)}",
                              clase_mensaje="error",
                              busqueda_realizada=False)

@main.route('/procesar-cancelacion', methods=['POST'])
def procesar_cancelacion():
    """Procesa la cancelación de una reserva"""
    id_reserva = request.form.get('id_reserva')
    
    if not id_reserva:
        return render_template('cancelar_reserva.html', 
                              mensaje="ID de reserva no proporcionado",
                              clase_mensaje="error")
    
    conn = None
    try:
        conn = obtener_conexion()
        cursor = cursor = conn.cursor()
        
        # Obtener datos de la reserva
        query = "SELECT * FROM reservas WHERE id = %s"
        cursor.execute(query, (id_reserva,))
        reserva = cursor.fetchone()
        
        if not reserva:
            raise ValueError("Reserva no encontrada")
        
        # Verificar si ya está cancelada
        if reserva['estado'] == 'cancelada':
            return render_template('cancelar_reserva.html', 
                                  mensaje="Esta reserva ya ha sido cancelada",
                                  clase_mensaje="error")
        
        # Actualizar estado de la reserva
        query_update_reserva = """
        UPDATE reservas 
        SET estado = 'cancelada' 
        WHERE id = %s
        """
        cursor.execute(query_update_reserva, (id_reserva,))
        
        # Actualizar disponibilidad de la habitación
        query_update_habitacion = """
        UPDATE habitaciones 
        SET disponibilidad = True 
        WHERE id = %s
        """
        cursor.execute(query_update_habitacion, (reserva['id_habitacion'],))
        
        # Confirmar cambios
        conn.commit()
        
        # Obtener datos para mostrar
        query = """
        SELECT r.*, h.tipo 
        FROM reservas r
        JOIN habitaciones h ON r.id_habitacion = h.id
        WHERE r.id = %s
        """
        cursor.execute(query, (id_reserva,))
        reserva_actualizada = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        # Enviar correo de confirmación de cancelación (opcional)
        try:
            # Aquí podrías implementar el envío de correo de cancelación
            pass
        except Exception as mail_error:
            print(f"Error al enviar correo de cancelación: {mail_error}")
        
        return render_template('cancelar_reserva.html', 
                              mensaje="Reserva cancelada exitosamente.",
                              clase_mensaje="success",
                              reserva=reserva_actualizada,
                              tipo_habitacion=reserva_actualizada['tipo'],
                              busqueda_realizada=True)
    
    except Exception as e:
        # En caso de error, hacer rollback
        if conn:
            conn.rollback()
            cursor.close()
            conn.close()
        
        print(f"Error al cancelar reserva: {e}")
        return render_template('cancelar_reserva.html', 
                              mensaje=f"Error al cancelar la reserva: {str(e)}",
                              clase_mensaje="error")