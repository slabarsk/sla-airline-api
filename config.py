import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///airline.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'cok-gizli-super-anahtar-sila')

    SWAGGER = {
        'title': 'Sla Airline API',
        'uiversion': 3,
        'description': 'Havayolu API dökümantasyonu',
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': "Bearer <token>"
            }
        }
    }
