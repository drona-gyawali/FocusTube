import traceback

from app.config.conf import (appwrite_apiKey, appwrite_bucketId,
                             appwrite_endpoint, appwrite_projectId)
from app.config.logger import get_logger
from appwrite.client import Client
from appwrite.exception import AppwriteException
from appwrite.id import ID
from appwrite.input_file import InputFile
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.services.storage import Storage

logger = get_logger("[app/config/appwrite_client]")


class AppwriteClient:
    def __init__(self):
        self.client = Client()
        self.client.set_endpoint(appwrite_endpoint)
        self.client.set_project(appwrite_projectId)
        self.client.set_key(appwrite_apiKey)
        self.storage = Storage(self.client)

    def get_client(self):
        return self.client

    def create_storage(self, temp_filename, current_user):
        try:
            result = self.storage.create_file(
                bucket_id=appwrite_bucketId,
                file_id=ID.unique(),
                file=InputFile.from_path(temp_filename),
                permissions=[
                    Permission.read(Role.any()),
                    Permission.write(Role.user(current_user.id)),
                ],
            )
        except AppwriteException as e:
            logger.error(
                f"Appwrite Error (upload): {e.message}\n{traceback.format_exc()}"
            )

        return result

    def delete_upload(self, file_id: str):
        try:
            self.storage.delete_file(bucket_id=appwrite_bucketId, file_id=file_id)
            logger.info(f"File with ID '{file_id}' deleted successfully.")
            return True
        except AppwriteException as e:
            logger.error(
                f"Appwrite Error (Delete): {e.message}\n{traceback.format_exc()}"
            )
            return False

    def getFilePreview(self, result):
        return f"{appwrite_endpoint}/storage/buckets/{result['bucketId']}/files/{result['$id']}/view?project={appwrite_projectId}&mode=admin"
