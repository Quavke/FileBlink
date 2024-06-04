
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
load_dotenv()

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

SECRET_AUTH = os.environ.get("SECRET_AUTH")
VT_API = os.environ.get("VT_API")


# key = Fernet.generate_key()
# with open("key.key", "wb") as key_file:
#     key_file.write(key)
