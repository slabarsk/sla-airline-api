from flask import Flask
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from .models import db
from .schemas import ma

def create_app():
    app = Flask(__name__)
    
    app.config.from_object('config.Config')
    
    db.init_app(app)
    ma.init_app(app)
    jwt = JWTManager(app)
    swagger = Swagger(app)
    
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    with app.app_context():
        db.create_all()
        
    return app