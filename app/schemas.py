from flask_marshmallow import Marshmallow
from .models import Flight, Passenger, Ticket

ma = Marshmallow()

# Uçuş DTO'su
class FlightSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Flight
        load_instance = True
        include_fk = True

# Yolcu DTO'su
class PassengerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Passenger
        load_instance = True

# Bilet DTO'su
class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = True
        include_fk = True

# Çeviricileri (Serializer) dışa aktarıyoruz
flight_schema = FlightSchema()
flights_schema = FlightSchema(many=True)
passenger_schema = PassengerSchema()
passengers_schema = PassengerSchema(many=True)
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)