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


### Setting up the Youtube API
youtube_key = os.getenv("YOUTUBE_APIKEY")
youtube_url = os.getenv("YOUTUBE_URL")
youtube_embeded = os.getenv("YOUTUBE_EMBEDED")

### Setting up the redis configuration
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_db = int(os.getenv("REDIS_DB", 0))
redis_password = os.getenv("REDIS_PASSWORD", None)
