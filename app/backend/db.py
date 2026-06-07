import psycopg2
from config import Config

def get_connection():
    return psycopg2.connect(Config.DATABASE_URL)

def test_tables():
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        return tables
    except Exception as e:
        print("Error al consultar tablas:", e)
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()