import psycopg2
from config import config

def get_connection():
    return psycopg2.connect(config.database_url)