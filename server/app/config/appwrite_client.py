from appwrite.client import Client
from appwrite.services.storage import Storage
from app.config.conf import appwrite_endpoint, appwrite_apiKey, appwrite_projectId

class AppwriteClient:
    def __init__(self):
        self.client = Client()
        self.client.set_endpoint(appwrite_endpoint)
        self.client.set_project(appwrite_projectId)
        self.client.set_key(appwrite_apiKey)
        self.storage = Storage(self.client)

    def get_client(self):
        return self.client

    def get_storage(self):
        return self.storage