from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from .services import FlightService
from .models import Flight

api_bp = Blueprint('api', __name__)

# --- 1. KİMLİK DOĞRULAMA ---
@api_bp.route('/login', methods=['POST'])
def login():
    """
    Sisteme Giriş ve Token Alma
    ---
    tags:
      - Authentication
    description: "Sisteme giriş yapıp yetki (token) aldığım uç nokta. Şimdilik test için kullanıcı adını 'admin', şifreyi '1234' olarak belirledim."
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: admin
            password:
              type: string
              example: 1234
    responses:
      200:
        description: "Giriş başarılı, token değerini dönüyorum."
      401:
        description: "Hatalı giriş yaptın."
    """
    data = request.get_json()
    
    # Sisteme yetkili giriş yapabilmek için basit bir kontrol
    if data.get('username') == 'admin' and str(data.get('password')) == '1234':
        access_token = create_access_token(identity='admin')
        return jsonify(access_token=access_token), 200
    
    return jsonify({"msg": "Hatalı kullanıcı adı veya şifre"}), 401

# --- 2. UÇUŞ EKLEME ---
@api_bp.route('/flights', methods=['POST'])
@jwt_required()
def add_flight():
    """
    Yeni Uçuş Ekleme Servisi
    ---
    tags:
      - Flights
    description: "Sisteme yeni bir uçuş eklediğim servis. İstenen gereksinimlere göre burası token ile korunuyor, yetkisiz işlem yapılamaz."
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - flight_number
            - date_from
            - date_to
            - airport_from
            - airport_to
            - duration
            - capacity
          properties:
            flight_number:
              type: string
              example: "TK1923"
            date_from:
              type: string
              example: "2026-04-01T10:00:00"
            date_to:
              type: string
              example: "2026-04-01T12:00:00"
            airport_from:
              type: string
              example: "IST"
            airport_to:
              type: string
              example: "ESB"
            duration:
              type: integer
              example: 120
            capacity:
              type: integer
              example: 180
    responses:
      201:
        description: "İşlem durumu (Transaction status)"
    """
    data = request.get_json()
    
    # Veritabanı işlemlerini doğrudan burada yapmıyorum, service katmanına yolluyorum
    response, status_code = FlightService.add_flight(data)
    
    return jsonify(response), status_code



    # --- 3. DOSYADAN TOPLU UÇUŞ EKLEME ---
@api_bp.route('/flights/upload', methods=['POST'])
@jwt_required()
def add_flights_by_file():
    """
    CSV Dosyasından Toplu Uçuş Ekleme
    ---
    tags:
      - Flights
    description: "Hazırladığım CSV dosyasını yükleyerek tek seferde birden fazla uçuşu sisteme kaydettiğim servis."
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: "Yüklenecek olan .csv uzantılı uçuş dosyası."
    responses:
      201:
        description: İşlem durumu ve dosya işleme sonucu döner.
    """
    if 'file' not in request.files:
        return jsonify({"transaction_status": "Error", "message": "Dosya bulunamadı"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"transaction_status": "Error", "message": "Dosya seçilmedi"}), 400
        
    if not file.filename.endswith('.csv'):
        return jsonify({"transaction_status": "Error", "message": "Sadece .csv uzantılı dosyalar kabul edilir."}), 400

    # Dosya işleme mantığını Service katmanına gönderiyoruz
    response, status_code = FlightService.add_flights_from_file(file)
    
    return jsonify(response), status_code


    # --- 4. UÇUŞ SORGULAMA ---
@api_bp.route('/flights/query', methods=['GET'])
def query_flights():
    """
    Uçuş Sorgulama ve Listeleme
    ---
    tags:
      - Flights
    description: "Kullanıcıların bilet almadan önce uygun uçuşları aradığı servis. Kimlik doğrulama gerektirmez. Sonuçlar 10'arlı sayfalar halinde gelir."
    parameters:
      - in: query
        name: date_from
        type: string
        required: true
        description: "Kalkış Tarihi (Örn: 2026-05-01T08:00:00)"
      - in: query
        name: airport_from
        type: string
        required: true
        description: "Kalkış Havaalanı (Örn: IST)"
      - in: query
        name: airport_to
        type: string
        required: true
        description: "Varış Havaalanı (Örn: ESB)"
      - in: query
        name: number_of_people
        type: integer
        required: true
        description: "Kişi Sayısı (Örn: 2)"
      - in: query
        name: page
        type: integer
        required: false
        default: 1
        description: "Sayfa Numarası"
    responses:
      200:
        description: "Mevcut uçuşların listesi."
    """

    date_from = request.args.get('date_from')
    airport_from = request.args.get('airport_from')
    airport_to = request.args.get('airport_to')
    
    try:
        number_of_people = int(request.args.get('number_of_people', 1))
        page = int(request.args.get('page', 1))
    except ValueError:
        return jsonify({"transaction_status": "Error", "message": "Geçersiz sayı formatı"}), 400

    if not all([date_from, airport_from, airport_to]):
         return jsonify({"transaction_status": "Error", "message": "Tarih ve güzergah bilgileri zorunludur."}), 400

    response, status_code = FlightService.query_flights(date_from, airport_from, airport_to, number_of_people, page)
    
    return jsonify(response), status_code


# --- 5. BİLET SATIN ALMA (BUY TICKET) ---
@api_bp.route('/tickets', methods=['POST'])
@jwt_required()
def buy_ticket():
    """
    Bilet Satın Alma İşlemi
    ---
    tags:
      - Tickets
    description: "Belirli bir uçuş için bilet satın alma işlemi. Uçuş kapasitesi düşürülür, yer yoksa hata döner. Kimlik doğrulama (Token) gereklidir."
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - flight_number
            - date
            - passenger_names
          properties:
            flight_number:
              type: string
              example: "TK101"
            date:
              type: string
              example: "2026-05-01"
            passenger_names:
              type: array
              items:
                type: string
              example: ["Sıla Barışık", "Çakır Tarçın"]
    responses:
      201:
        description: İşlem durumu ve üretilen bilet numaraları döner.
      400:
        description: Sold out veya hatalı istek durumu.
    """
    data = request.get_json()
    response, status_code = FlightService.buy_ticket(data)
    
    return jsonify(response), status_code

    
    # --- 6. CHECK-IN YAPMA ---
@api_bp.route('/checkin', methods=['POST'])
def check_in():
    """
    Check-in İşlemi
    ---
    tags:
      - Tickets
    description: "Bilet almış bir yolcuya uçuş için koltuk ataması yapar. Kimlik doğrulama gerektirmez."
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - flight_number
            - Date
            - passenger_name
          properties:
            flight_number:
              type: string
              example: "TK101"
            Date:
              type: string
              example: "2026-05-01"
            passenger_name:
              type: string
              example: "Sıla Barışık"
    responses:
      200:
        description: İşlem durumu döner.
    """
    data = request.get_json()
    response, status_code = FlightService.check_in(data)
    return jsonify(response), status_code

# --- 7. YOLCU LİSTESİ SORGULAMA ---
@api_bp.route('/flights/passengers', methods=['GET'])
@jwt_required()
def passenger_list():
    """
    Uçuş Yolcu Listesi
    ---
    tags:
      - Flights
    description: "Bir uçuşa ait yolcuları ve koltuk numaralarını listeler. Token (kimlik doğrulama) gereklidir. Sayfalama mevcuttur."
    security:
      - Bearer: []
    parameters:
      - in: query
        name: flight_number
        type: string
        required: true
        description: "Uçuş Numarası (Örn: TK101)"
      - in: query
        name: date
        type: string
        required: true
        description: "Tarih (Örn: 2026-05-01)"
      - in: query
        name: page
        type: integer
        required: false
        default: 1
        description: "Sayfa Numarası"
    responses:
      200:
        description: Yolcu listesi döner.
    """
    flight_number = request.args.get('flight_number')
    page = request.args.get('page', 1, type=int)
    
    if not flight_number:
        return jsonify({"transaction_status": "Error", "message": "Uçuş numarası zorunludur."}), 400
        
    response, status_code = FlightService.get_passenger_list(flight_number, page)
    return jsonify(response), status_code

    # --- 8. UÇUŞ TARİHLERİ ---
@api_bp.route('/flights/dates', methods=['GET'])
def get_flight_dates():
    airport_from = request.args.get('airport_from')
    airport_to   = request.args.get('airport_to')
    if not airport_from or not airport_to:
        return jsonify({"dates": []})
    flights = Flight.query.filter_by(
        airport_from=airport_from,
        airport_to=airport_to
    ).all()
    dates = sorted([f.date_from.strftime('%Y-%m-%dT%H:%M:%S') for f in flights])
    return jsonify({"dates": dates})