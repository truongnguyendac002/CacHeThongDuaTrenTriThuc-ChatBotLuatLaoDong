from flask import Flask
from app.config import Config
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    
    # Đăng ký các Blueprint
    from app.routes import main
    app.register_blueprint(main)
    
    return app
