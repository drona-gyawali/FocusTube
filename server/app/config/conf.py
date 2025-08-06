import os

from dotenv import load_dotenv

load_dotenv()

### Setting up the database
username = os.getenv("DATABASE_USERNAME")
password = os.getenv("DATABASE_PASSWORD")
db_name = os.getenv("DATABASE_NAME")

### Setting up the jwt tokens
secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")

### Setting up the appwrite storage
appwrite_endpoint = os.getenv("APPWRITE_URL")
appwrite_projectId = os.getenv("APPWRITE_PROJECT_ID")
appwrite_apiKey = os.getenv("APPWRITE_APIKEY")
appwrite_bucketId = os.getenv("APPWRITE_BUCKETID")
