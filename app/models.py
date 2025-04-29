from app import db

class Habitacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    disponibilidad = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Habitacion {self.tipo}>'
