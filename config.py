import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Azure Storage settings
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_BLOB_CONTAINER = os.environ.get('AZURE_BLOB_CONTAINER')
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Model settings
    MODEL_PATH = os.path.join('models', 'tubercnn_v2.h5')
    
    # Videos
    VIDEO_URL_1 = os.environ.get('VIDEO_URL_1')
    VIDEO_URL_2 = os.environ.get('VIDEO_URL_2')