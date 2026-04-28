import psycopg2
from config import load_config

def get_connection():
    try:
        config = load_config()
        conn = psycopg2.connect(**config)
        return conn
    except Exception:
        return None