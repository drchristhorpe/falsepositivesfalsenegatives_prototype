"""
Configuration settings for the False Positives/Negatives Database
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # API Configuration
    SHEETY_API_URL = os.getenv('SHEETY_API_URL')
    SHEETY_TOKEN = os.getenv('SHEETY_TOKEN')
    MAILJET_API_KEY = os.getenv('MAILJET_API_KEY')
    MAILJET_SECRET_KEY = os.getenv('MAILJET_SECRET_KEY')
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
    
    # Application Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    WTF_CSRF_ENABLED = True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}