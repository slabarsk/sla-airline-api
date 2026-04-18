from .models import db, Flight, Passenger, Ticket
from datetime import datetime
import csv
import io
import uuid

class FlightService:
    
    @staticmethod
    def add_flight(data):
        try:
            date_from = datetime.fromisoformat(data['date_from'])
            date_to = datetime.fromisoformat(data['date_to'])
            
            new_flight = Flight(
                flight_number=data['flight_number'],
                date_from=date_from,
                date_to=date_to,
                airport_from=data['airport_from'],
                airport_to=data['airport_to'],
                duration=data['duration'],
                capacity=data['capacity']
            )
            db.session.add(new_flight)
            db.session.commit()
            return {"transaction_status": "Success", "message": "Uçuş başarıyla eklendi"}, 201
        except Exception as e:
            db.session.rollback()
            return {"transaction_status": "Error", "message": str(e)}, 400

    @staticmethod
    def add_flights_from_file(file):
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.DictReader(stream)
            added_count = 0
            
            for row in csv_input:
                date_from = datetime.fromisoformat(row['date_from'])
                date_to = datetime.fromisoformat(row['date_to'])
                
                new_flight = Flight(
                    flight_number=row['flight_number'],
                    date_from=date_from,
                    date_to=date_to,
                    airport_from=row['airport_from'],
                    airport_to=row['airport_to'],
                    duration=int(row['duration']),
                    capacity=int(row['capacity'])
                )
                db.session.add(new_flight)
                added_count += 1
                
            db.session.commit()
            return {
                "transaction_status": "Success", 
                "file_processes_status": f"{added_count} uçuş dosyadan başarıyla eklendi."
            }, 201
        except Exception as e:
            db.session.rollback()
            return {
                "transaction_status": "Error", 
                "file_processes_status": f"Dosya işlenirken hata oluştu: {str(e)}"
            }, 400
    @staticmethod
    def query_flights(date_from, airport_from, airport_to, number_of_people, page=1):
        try:
            search_date = datetime.fromisoformat(date_from).date()
            start_dt = datetime.combine(search_date, datetime.min.time())
            end_dt   = datetime.combine(search_date, datetime.max.time())

            query = Flight.query.filter(
                Flight.airport_from == airport_from,
                Flight.airport_to == airport_to,
                Flight.capacity >= number_of_people,
                Flight.date_from >= start_dt,
                Flight.date_from <= end_dt,
            ).order_by(Flight.date_from.asc())

            paginated_flights = query.paginate(page=page, per_page=10, error_out=False)

            flight_list = [{
                "Flight number": f.flight_number,
                "duration": f.duration,
                "date_from": f.date_from.strftime("%H:%M"),
                "date_to": f.date_to.strftime("%H:%M")
            } for f in paginated_flights.items]

            return {
                "available_flights": flight_list,
                "current_page": paginated_flights.page,
                "total_pages": paginated_flights.pages
            }, 200
        except Exception as e:
            return {"transaction_status": "Error", "message": str(e)}, 400

    @staticmethod
    def buy_ticket(data):
        try:
            flight_number = data.get('flight_number')
            passenger_names = data.get('passenger_names', [])
            
            if not flight_number or not passenger_names:
                return {"transaction_status": "Error", "message": "Uçuş numarası ve yolcu isimleri zorunludur."}, 400
                
            flight = Flight.query.filter_by(flight_number=flight_number).first()
            if not flight:
                return {"transaction_status": "Error", "message": "Uçuş bulunamadı."}, 404
                
            number_of_tickets = len(passenger_names)
            if flight.capacity < number_of_tickets:
                return {"transaction_status": "Error", "message": "Sold out. Uçuşta yeterli koltuk bulunmuyor."}, 400
                
            ticket_numbers = []
            for name in passenger_names:
                new_passenger = Passenger(name=name)
                db.session.add(new_passenger)
                db.session.flush() 
                
                ticket_num = str(uuid.uuid4())[:8].upper() 
                new_ticket = Ticket(
                    ticket_number=ticket_num, 
                    flight_id=flight.id, 
                    passenger_id=new_passenger.id
                )
                db.session.add(new_ticket)
                ticket_numbers.append(ticket_num)
                
            flight.capacity -= number_of_tickets
            db.session.commit()
            
            return {
                "transaction_status": "Success", 
                "ticket_numbers": ticket_numbers,
                "message": f"{number_of_tickets} bilet başarıyla satın alındı. Kalan kapasite: {flight.capacity}"
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"transaction_status": "Error", "message": str(e)}, 500

    @staticmethod
    def check_in(data):
        try:
            flight_number = data.get('flight_number')
            passenger_name = data.get('passenger_name')
            
            if not flight_number or not passenger_name:
                return {"transaction_status": "Error", "message": "Uçuş numarası ve yolcu adı zorunludur."}, 400
                
            flight = Flight.query.filter_by(flight_number=flight_number).first()
            if not flight:
                return {"transaction_status": "Error", "message": "Uçuş bulunamadı."}, 404
                
            passenger = Passenger.query.filter_by(name=passenger_name).first()
            if not passenger:
                return {"transaction_status": "Error", "message": "Yolcu bulunamadı."}, 404
                
            ticket = Ticket.query.filter_by(flight_id=flight.id, passenger_id=passenger.id).first()
            if not ticket:
                return {"transaction_status": "Error", "message": "Bu uçuş için biletiniz bulunmuyor."}, 404
                
            if ticket.seat_number:
                return {"transaction_status": "Error", "message": f"Zaten check-in yapılmış. Koltuğunuz: {ticket.seat_number}"}, 400
                
            assigned_seats_count = Ticket.query.filter(Ticket.flight_id == flight.id, Ticket.seat_number != None).count()
            new_seat = f"{assigned_seats_count + 1}A"
            
            ticket.seat_number = new_seat
            db.session.commit()
            
            return {"transaction_status": "Success", "message": f"Check-in başarılı. Koltuk numaranız: {new_seat}"}, 200
        except Exception as e:
            db.session.rollback()
            return {"transaction_status": "Error", "message": str(e)}, 500

    @staticmethod
    def get_passenger_list(flight_number, page=1):
        try:
            flight = Flight.query.filter_by(flight_number=flight_number).first()
            if not flight:
                return {"transaction_status": "Error", "message": "Uçuş bulunamadı."}, 404
                
            query = db.session.query(Ticket, Passenger).join(Passenger).filter(Ticket.flight_id == flight.id)
            paginated = query.paginate(page=page, per_page=10, error_out=False)
            
            passenger_list = []
            for t, p in paginated.items:
                passenger_list.append({
                    "Passenger Name": p.name,
                    "Seat": t.seat_number if t.seat_number else "Check-in yapılmadı"
                })
                
            return {
                "transaction_status": "Success",
                "passengers": passenger_list,
                "current_page": paginated.page,
                "total_pages": paginated.pages
            }, 200
        except Exception as e:
            return {"transaction_status": "Error", "message": str(e)}, 500