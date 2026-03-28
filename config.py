import os

class Config:
    # Şimdilik lokalde çalışıyorum, buluta atarken burayı güncelleyeceğim
    SQLALCHEMY_DATABASE_URI = 'sqlite:///airline.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT yetkilendirmesi için gizli anahtarım
    JWT_SECRET_KEY = 'cok-gizli-super-anahtar-sila'
    
    # Swagger arayüzü ayarlarım
    SWAGGER = {
        'title': 'Sla Airline API',
        'uiversion': 3,
        'description': 'Havayolu API dökümantasyonu',
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': "Giriş yaptıktan sonra aldığın token'ı 'Bearer ' yazıp bir boşluk bıraktıktan sonra buraya yapıştırabilirsin."
            }
        }
    }