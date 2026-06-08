# Nos ayudara a registrar las operaciones que se realizan en el sistema, como la creación de un nuevo asociado, la actualización de información, etc.
# Esto nos permitirá tener un historial de las acciones realizadas por los usuarios y facilitará la auditoría y el seguimiento de las actividades en el sistema.
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