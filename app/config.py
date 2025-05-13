import os

class Config:
    # Cấu hình database
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
    DB_NAME = os.environ.get('DB_NAME', 'chatbot_luat_lao_dong_2')
    
    # Cấu hình ứng dụng
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Ngưỡng tối thiểu để xác định trường hợp tương đồng
    SIMILARITY_THRESHOLD = 0.6
    GEMINI_THRESHOLD = 0.9
    GEMINI_API_KEY = "AIzaSyCciaXSlbJaIxL0t3LUJ__dMOWQhihOHnQ"

