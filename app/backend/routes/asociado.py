from flask import Blueprint, render_template, request, Response
## Agregamos Response para la ruta de descarga de extracto en formato CSV
import csv
from io import StringIO
from db import get_connection

asociado_bp = Blueprint(
    'asociado',
    __name__
)

CEDULA_PRUEBA = '12345678' ## Se usa porque aun no hay un sistema de autenticación implementado

## Ruta para mostrar los datos del asociado
@asociado_bp.route('/mis_datos')
def mis_datos():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                cedula,
                nombre,
                apellido,
                telefono,
                correo,
                direccion,
                municipio,
                fecha_afiliacion,
                fecha_nacimiento,
                estado
            FROM asociado
            WHERE cedula = %s
        """, (CEDULA_PRUEBA,))

        asociado = cur.fetchone()

        return render_template(
            'mis_datos.html',
            asociado=asociado
        )

    except Exception as e:

        return str(e)

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Ruta para mostrar las cuentas del asociado + el saldo calculado a partir de los movimientos asociados a cada cuenta
@asociado_bp.route('/mis_cuentas')
def mis_cuentas():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                c.numero_cuenta,
                c.fecha_apertura,
                c.estado,
                c.codigo_agencia,

                COALESCE(
                    SUM(
                        CASE

                            WHEN m.tipo IN (
                                'depósito',
                                'transferencia entrante'
                            )
                            THEN m.valor

                            WHEN m.tipo IN (
                                'retiro',
                                'transferencia saliente'
                            )
                            THEN -m.valor

                            ELSE 0

                        END
                    ),
                    0
                ) AS saldo

            FROM cuenta_ahorro c

            LEFT JOIN movimiento m
                ON c.numero_cuenta =
                   m.numero_cuenta

            WHERE c.cedula_asociado = %s

            GROUP BY
                c.numero_cuenta,
                c.fecha_apertura,
                c.estado,
                c.codigo_agencia

            ORDER BY c.numero_cuenta
        """, (CEDULA_PRUEBA,))

        cuentas = cur.fetchall()

        return render_template(
            'mis_cuentas.html',
            cuentas=cuentas
        )

    except Exception as e:

        return str(e)

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Ruta para mostrar los créditos del asociado
@asociado_bp.route('/mis_creditos')
def mis_creditos():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                numero_radicado,
                valor_solicitado,
                valor_aprobado,
                plazo,
                tasa_interes,
                linea_credito,
                estado
            FROM credito
            WHERE cedula_asociado = %s
            ORDER BY numero_radicado
        """, (CEDULA_PRUEBA,))

        creditos = cur.fetchall()

        return render_template(
            'mis_creditos.html',
            creditos=creditos
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Ruta para mostrar el extracto del asociado con filtros opcionales
@asociado_bp.route('/extracto')
def extracto():

    conn = None
    cur = None

    try:

        fecha_inicio = request.args.get(
            'fecha_inicio'
        )

        fecha_fin = request.args.get(
            'fecha_fin'
        )

        canal = request.args.get(
            'canal'
        )

        conn = get_connection()
        cur = conn.cursor()

        consulta = """
            SELECT
                m.id_transaccion,
                m.fecha_hora,
                m.tipo,
                m.valor,
                m.canal,
                m.numero_cuenta
            FROM movimiento m
            JOIN cuenta_ahorro c
                ON m.numero_cuenta =
                   c.numero_cuenta
            WHERE c.cedula_asociado = %s
        """

        parametros = [CEDULA_PRUEBA]

        if fecha_inicio:
            consulta += """
                AND m.fecha_hora >= %s
            """
            parametros.append(fecha_inicio)

        if fecha_fin:
            consulta += """
                AND m.fecha_hora <= %s
            """
            parametros.append(fecha_fin)

        if canal:
            consulta += """
                AND m.canal = %s
            """
            parametros.append(canal)

        consulta += """
            ORDER BY m.fecha_hora DESC
        """

        cur.execute(
            consulta,
            tuple(parametros)
        )

        movimientos = cur.fetchall()

        return render_template(
            'extracto.html',
            movimientos=movimientos
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Ruta para descargar el extracto del asociado en formato CSV con los mismos filtros que la ruta anterior
@asociado_bp.route('/extracto/csv')
def exportar_extracto_csv():

    conn = None
    cur = None

    try:

        fecha_inicio = request.args.get(
            'fecha_inicio'
        )

        fecha_fin = request.args.get(
            'fecha_fin'
        )

        canal = request.args.get(
            'canal'
        )

        conn = get_connection()
        cur = conn.cursor()

        consulta = """
            SELECT
                m.id_transaccion,
                m.fecha_hora,
                m.tipo,
                m.valor,
                m.canal,
                m.numero_cuenta
            FROM movimiento m
            JOIN cuenta_ahorro c
                ON m.numero_cuenta =
                   c.numero_cuenta
            WHERE c.cedula_asociado = %s
        """

        parametros = [CEDULA_PRUEBA]

        if fecha_inicio:
            consulta += """
                AND m.fecha_hora >= %s
            """
            parametros.append(fecha_inicio)

        if fecha_fin:
            consulta += """
                AND m.fecha_hora <= %s
            """
            parametros.append(fecha_fin)

        if canal:
            consulta += """
                AND m.canal = %s
            """
            parametros.append(canal)

        consulta += """
            ORDER BY m.fecha_hora DESC
        """

        cur.execute(
            consulta,
            tuple(parametros)
        )

        movimientos = cur.fetchall()

        output = StringIO()

        writer = csv.writer(output)

        writer.writerow([
            'ID Transaccion',
            'Fecha Hora',
            'Tipo',
            'Valor',
            'Canal',
            'Numero Cuenta'
        ])

        for movimiento in movimientos:

            writer.writerow(movimiento)

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition':
                'attachment; filename=extracto.csv'
            }
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()