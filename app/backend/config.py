import os
from dotenv import load_dotenv

load_dotenv()

class config:
    secret_key = os.getenv('secret_key', 'coovalluna_clave_temporal')
    database_url = os.getenv('database_url')
    debug = os.getenv('debug', 'true').lower() == 'true'