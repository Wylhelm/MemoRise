import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///memory.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Azure AI credentials
    TEXT_ANALYTICS_KEY = "beb426be64af4d5181ecff4801816f72"
    TEXT_ANALYTICS_ENDPOINT = "https://pylanguage.cognitiveservices.azure.com/"
    SPEECH_KEY = "9c84dbbed4474be4b5f2dfbfcc53b5d3"
    SPEECH_REGION = "eastus"
