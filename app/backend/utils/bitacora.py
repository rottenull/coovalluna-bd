# app/backend/utils/bitacora.py

from db import get_connection

def registrar_bitacora(usuario, operacion):

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO bitacora(
                usuario,
                operacion
            )
            VALUES (%s,%s)
        """, (
            usuario,
            operacion
        ))

        conn.commit()

    except Exception as e:

        print(f'Error bitácora: {e}')

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()