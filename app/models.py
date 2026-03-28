from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Veritabanı nesnemizi oluşturuyoruz
db = SQLAlchemy()

# Uçuş Tablosu
class Flight(db.Model):
    __tablename__ = 'flights'
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(50), unique=True, nullable=False)
    date_from = db.Column(db.DateTime, nullable=False)
    date_to = db.Column(db.DateTime, nullable=False)
    airport_from = db.Column(db.String(10), nullable=False)
    airport_to = db.Column(db.String(10), nullable=False)
    duration = db.Column(db.Integer, nullable=False) # Dakika cinsinden
    capacity = db.Column(db.Integer, nullable=False)
    
    # Biletler tablosu ile ilişki
    tickets = db.relationship('Ticket', backref='flight', lazy=True)

# Yolcu Tablosu
class Passenger(db.Model):
    __tablename__ = 'passengers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Biletler tablosu ile ilişki
    tickets = db.relationship('Ticket', backref='passenger', lazy=True)

# Bilet Tablosu
class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(100), unique=True, nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    passenger_id = db.Column(db.Integer, db.ForeignKey('passengers.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=True) # Check-in sırasında atanacak
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)