from flask_mail import Message
from flask import render_template
from . import mail
import os

def send_reservation_confirmation(reservation_data):
    """
    Envía correo de confirmación de reserva al cliente y al administrador
    
    Args:
        reservation_data: Diccionario con los datos de la reserva
    """
    # Email al cliente
    send_client_confirmation(reservation_data)
    
    # Email al administrador
    send_admin_notification(reservation_data)

def send_client_confirmation(data):
    """Envía correo de confirmación al cliente"""
    subject = f"Confirmación de reserva #{data['numero_reserva']} - Bio Palma Hotel"
    
    msg = Message(
        subject=subject,
        recipients=[data['email']]
    )
    
    # Contenido HTML del correo
    msg.html = render_template('emails/confirmacion_cliente.html', **data)
    
    # Contenido de texto plano (alternativo)
    msg.body = f"""
    ¡Reserva Confirmada! #{data['numero_reserva']}
    
    Hola {data['nombre']},
    
    Tu reserva en Bio Palma Hotel ha sido confirmada.
    
    Detalles de la reserva:
    - Número de reserva: {data['numero_reserva']}
    - Fecha de entrada: {data['entrada']}
    - Fecha de salida: {data['salida']}
    - Total pagado: ${data['precio_total']}
    - Método de pago: {data['metodo_pago']}
    
    Gracias por elegir Bio Palma Hotel.
    """
    
    mail.send(msg)

def send_admin_notification(data):
    """Envía notificación al administrador"""
    admin_email = os.environ.get('ADMIN_EMAIL')
    if not admin_email:
        return
    
    subject = f"Nueva reserva: #{data['numero_reserva']} - {data['nombre']}"
    
    msg = Message(
        subject=subject,
        recipients=[admin_email]
    )
    
    # Contenido HTML
    msg.html = render_template('emails/notificacion_admin.html', **data)
    
    # Contenido texto plano
    msg.body = f"""
    NUEVA RESERVA - #{data['numero_reserva']}
    
    Cliente: {data['nombre']}
    Email: {data['email']}
    Teléfono: {data['telefono']}
    
    Detalles:
    - Entrada: {data['entrada']}
    - Salida: {data['salida']}
    - Huéspedes: {data.get('huespedes', 1)}
    - Total: ${data['precio_total']}
    - Método de pago: {data['metodo_pago']}
    
    Comentarios: {data.get('comentarios', 'Ninguno')}
    """
    
    mail.send(msg)