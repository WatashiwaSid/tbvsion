# utils/model_downloader.py
import os
import logging
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = ['models', 'static/uploads', 'temp']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Directory '{directory}' ensured")

def download_model_from_blob():
    """Download model from Azure Blob Storage if not present locally"""
    model_path = "models/tubercnn_v2.h5"
    
    # Check if model already exists
    if os.path.exists(model_path):
        logger.info(f"Model already exists at {model_path}")
        return model_path
    
    # Ensure models directory exists
    os.makedirs('models', exist_ok=True)
    
    try:
        # Get connection string from environment
        connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        if not connection_string:
            logger.error("AZURE_STORAGE_CONNECTION_STRING not found in environment variables")
            raise ValueError("Azure Storage connection string not configured")
        
        # Initialize blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Download model from blob storage
        container_name = "models"  # Your container name
        blob_name = "tubercnn_v2.h5"     # Your blob name
        
        logger.info(f"Downloading model from blob storage: {container_name}/{blob_name}")
        
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        # Download and save model
        with open(model_path, 'wb') as file:
            download_stream = blob_client.download_blob()
            file.write(download_stream.readall())
        
        logger.info(f"Model downloaded successfully to {model_path}")
        return model_path
        
    except ResourceNotFoundError:
        logger.error(f"Model blob not found in container '{container_name}'")
        raise FileNotFoundError(f"Model not found in Azure Blob Storage")
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        raise

def initialize_app_storage():
    """Initialize all required directories and download model"""
    try:
        ensure_directories()
        model_path = download_model_from_blob()
        logger.info("App storage initialization completed successfully")
        return model_path
    except Exception as e:
        logger.error(f"Failed to initialize app storage: {str(e)}")
        raise

# Updated app.py - Add this at the top after imports
from utils.model_downloader import initialize_app_storage

# At the start of your Flask app initialization
try:
    model_path = initialize_app_storage()
    logger.info(f"Using model at: {model_path}")
except Exception as e:
    logger.error(f"Failed to initialize storage: {e}")
    # You might want to exit or use a fallback strategy
    raise