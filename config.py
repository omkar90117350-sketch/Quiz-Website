import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'quizr-saas-secret-2024')
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'quizr.db')
    OPEN_TRIVIA_API = "https://opentdb.com/api.php"
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyDvJhiICepc02o2uaZb3eOvWbKL9lhZ-X0')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'MMCOE@2006Karvenagar')
    DEBUG = True
