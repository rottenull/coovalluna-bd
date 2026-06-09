from flask import Blueprint, render_template, request, Response, session, redirect, url_for, flash
import csv
from io import StringIO
from db import get_connection


asociado_bp = Blueprint(
    'asociado',
    __name__
)

def obtener_cedula_asociado():
    return session.get('cedula_asociado')


@asociado_bp.route('/mis_datos')
def mis_datos():

    cedula = obtener_cedula_asociado()

    if not cedula:
        flash('Debes iniciar sesión como asociado')
        return redirect(url_for('auth.login'))

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
        """, (cedula,))

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


@asociado_bp.route('/mis_cuentas')
def mis_cuentas():

    cedula = obtener_cedula_asociado()

    if not cedula:
        flash('Debes iniciar sesión como asociado')
        return redirect(url_for('auth.login'))

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
                ON c.numero_cuenta = m.numero_cuenta

            WHERE c.cedula_asociado = %s

            GROUP BY
                c.numero_cuenta,
                c.fecha_apertura,
                c.estado,
                c.codigo_agencia

            ORDER BY c.numero_cuenta
        """, (cedula,))

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


@asociado_bp.route('/mis_creditos')
def mis_creditos():

    cedula = obtener_cedula_asociado()

    if not cedula:
        flash('Debes iniciar sesión como asociado')
        return redirect(url_for('auth.login'))

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
        """, (cedula,))

        creditos = cur.fetchall()

        return render_template(
            'mis_creditos.html',
            creditos=creditos
        )

    except Exception as e:
        return str(e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

## Rutas para asociados: beneficiarios, extracto, exportar extracto CSV
@asociado_bp.route('/mis_beneficiarios')
def mis_beneficiarios():

    cedula = obtener_cedula_asociado()

    if not cedula:
        flash('Debes iniciar sesión como asociado')
        return redirect(url_for('auth.login'))

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                documento,
                nombre,
                parentesco,
                porcentaje,
                telefono
            FROM beneficiario
            WHERE cedula_asociado = %s
            ORDER BY nombre
        """, (cedula,))

        beneficiarios = cur.fetchall()

        return render_template(
            'mis_beneficiarios.html',
            beneficiarios=beneficiarios
        )

    except Exception as e:
        return str(e)

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()


@asociado_bp.route('/extracto')
def extracto():

    cedula = obtener_cedula_asociado()

    if not cedula:
        flash('Debes iniciar sesión como asociado')
        return redirect(url_for('auth.login'))

    conn = None
    cur = None

    try:

        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        canal = request.args.get('canal')
        numero_cuenta = request.args.get('numero_cuenta')
        tipo_movimiento = request.args.get('tipo_movimiento')

        conn = get_connection()
        cur = conn.cursor()

        # Cuentas del asociado para el combo

        cur.execute("""
            SELECT numero_cuenta
            FROM cuenta_ahorro
            WHERE cedula_asociado = %s
            ORDER BY numero_cuenta
        """, (cedula,))

        cuentas = cur.fetchall()

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
                ON m.numero_cuenta = c.numero_cuenta
            WHERE c.cedula_asociado = %s
        """

        parametros = [cedula]

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

        if numero_cuenta:
            consulta += """
                AND m.numero_cuenta = %s
            """
            parametros.append(numero_cuenta)

        if tipo_movimiento:
            consulta += """
                AND m.tipo = %s
            """
            parametros.append(tipo_movimiento)

        consulta += """
            ORDER BY m.fecha_hora DESC
        """

        cur.execute(
            consulta,
            tuple(parametros)
        )

        movimientos = cur.fetchall()

        saldo = 0

        for movimiento in movimientos:

            tipo = movimiento[2]
            valor = float(movimiento[3])

            if tipo in [
                'depósito',
                'transferencia entrante'
            ]:
                saldo += valor

            elif tipo in [
                'retiro',
                'transferencia saliente'
            ]:
                saldo -= valor

        return render_template(
            'extracto.html',
            movimientos=movimientos,
            cuentas=cuentas,
            saldo=saldo
        )

    except Exception as e:
        return str(e)

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


@asociado_bp.route('/extracto/csv')
def exportar_extracto_csv():

    cedula = obtener_cedula_asociado()

    if not cedula:
        flash('Debes iniciar sesión como asociado')
        return redirect(url_for('auth.login'))

    conn = None
    cur = None

    try:

        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        canal = request.args.get('canal')
        numero_cuenta = request.args.get('numero_cuenta')
        tipo_movimiento = request.args.get('tipo_movimiento')

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
                ON m.numero_cuenta = c.numero_cuenta
            WHERE c.cedula_asociado = %s
        """

        parametros = [cedula]

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

        if numero_cuenta:
            consulta += """
                AND m.numero_cuenta = %s
            """
            parametros.append(numero_cuenta)

        if tipo_movimiento:
            consulta += """
                AND m.tipo = %s
            """
            parametros.append(tipo_movimiento)

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

    except Exception as e:
        return str(e)

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Ruta para que el asociado solicite actualización de datos a un asesor
@asociado_bp.route('/solicitar_actualizacion')
def solicitar_actualizacion():

    cedula = obtener_cedula_asociado()

    if not cedula:
        flash('Debes iniciar sesión como asociado')
        return redirect(url_for('auth.login'))

    return render_template(
        'solicitar_actualizacion.html'
    )

## Ruta para guardar la solicitud de actualización de datos del asociado
@asociado_bp.route(
    '/solicitar_actualizacion/guardar',
    methods=['POST']
)
def guardar_solicitud_actualizacion():

    cedula = obtener_cedula_asociado()

    if not cedula:
        flash('Debes iniciar sesión como asociado')
        return redirect(url_for('auth.login'))

    conn = None
    cur = None

    try:

        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        direccion = request.form.get('direccion')
        municipio = request.form.get('municipio')

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO solicitud_actualizacion(
                cedula_asociado,
                telefono_nuevo,
                correo_nuevo,
                direccion_nueva,
                municipio_nuevo
            )
            VALUES (%s,%s,%s,%s,%s)
        """,
        (
            cedula,
            telefono,
            correo,
            direccion,
            municipio
        ))

        conn.commit()

        flash(
            'Solicitud enviada correctamente. Queda pendiente de aprobación.'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al registrar solicitud: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('auth.dashboard_asociado')
    )