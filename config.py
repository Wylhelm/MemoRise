import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///memory.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Azure AI credentials
    TEXT_ANALYTICS_KEY = "your azure key"
    TEXT_ANALYTICS_ENDPOINT = "your azure endpoint"
