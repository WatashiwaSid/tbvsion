
import os
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from config import Config

class AzureStorage:
    def __init__(self):
        self.connection_string = Config.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = Config.AZURE_BLOB_CONTAINER
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
        
    def upload_file(self, file_path, blob_name=None):
        """Upload a file to Azure Blob Storage"""
        if blob_name is None:
            blob_name = os.path.basename(file_path)
            
        blob_client = self.container_client.get_blob_client(blob_name)
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
            
        return blob_client.url
    
    def get_sas_url(self, blob_name, expiry_hours=24):
        """Generate a SAS URL for a blob"""
        blob_client = self.container_client.get_blob_client(blob_name)
        
        sas_token = generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=self.blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
        )
        
        return f"{blob_client.url}?{sas_token}"
    
    def list_all_blobs(self, name_starts_with=None):
        """List all blobs in the container"""
        blobs = self.container_client.list_blobs(name_starts_with=name_starts_with)
        return [blob.name for blob in blobs]