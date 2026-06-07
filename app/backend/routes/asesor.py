from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection

asesor_bp = Blueprint('asesor', __name__)


## Listamos los asociados
@asesor_bp.route('/asociados')
def asociados():

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
                municipio,
                fecha_afiliacion,
                estado
            FROM asociado
            ORDER BY nombre
        """)

        asociados = cur.fetchall()

        return render_template(
            'asociados.html',
            asociados=asociados
        )

    except Exception as e:

        flash(f'Error al consultar asociados: {e}')

        return render_template(
            'asociados.html',
            asociados=[]
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Formulario nuevo asociado
@asesor_bp.route('/asociados/nuevo')
def nuevo_asociado():

    return render_template(
        'nuevo_asociado.html'
    )

## Creamos un nuevo asociado
@asesor_bp.route('/asociados/crear', methods=['POST'])
def crear_asociado():

    conn = None
    cur = None

    try:

        cedula = request.form.get('cedula')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        direccion = request.form.get('direccion')
        municipio = request.form.get('municipio')
        fecha_afiliacion = request.form.get('fecha_afiliacion')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        estado = request.form.get('estado')

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO asociado(
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
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
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
        ))

        conn.commit()

        flash('Asociado registrado correctamente')

    except Exception as e:

        if conn:
            conn.rollback()

        flash(f'Error al registrar asociado: {e}')

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.asociados')
    )

## Editamos un asociado
@asesor_bp.route('/asociados/editar/<cedula>')
def editar_asociado(cedula):

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

        if not asociado:
            flash('Asociado no encontrado')
            return redirect(
                url_for('asesor.asociados')
            )

        return render_template(
            'editar_asociado.html',
            asociado=asociado
        )

    except Exception as e:

        flash(f'Error al cargar asociado: {e}')

        return redirect(
            url_for('asesor.asociados')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Actualizamos un asociado
@asesor_bp.route('/asociados/actualizar/<cedula>', methods=['POST'])
def actualizar_asociado(cedula):

    conn = None
    cur = None

    try:

        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        direccion = request.form.get('direccion')
        municipio = request.form.get('municipio')
        fecha_afiliacion = request.form.get('fecha_afiliacion')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        estado = request.form.get('estado')

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE asociado
            SET
                nombre = %s,
                apellido = %s,
                telefono = %s,
                correo = %s,
                direccion = %s,
                municipio = %s,
                fecha_afiliacion = %s,
                fecha_nacimiento = %s,
                estado = %s
            WHERE cedula = %s
        """,
        (
            nombre,
            apellido,
            telefono,
            correo,
            direccion,
            municipio,
            fecha_afiliacion,
            fecha_nacimiento,
            estado,
            cedula
        ))

        conn.commit()

        flash('Asociado actualizado correctamente')

    except Exception as e:

        if conn:
            conn.rollback()

        flash(f'Error al actualizar asociado: {e}')

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.asociados')
    )

## Cambiamos el estado de un asociado
@asesor_bp.route('/asociados/cambiar_estado/<cedula>', methods=['POST'])
def cambiar_estado_asociado(cedula):

    conn = None
    cur = None

    try:

        nuevo_estado = request.form.get('estado')

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE asociado
            SET estado = %s
            WHERE cedula = %s
        """,
        (
            nuevo_estado,
            cedula
        ))

        conn.commit()

        flash('Estado actualizado correctamente')

    except Exception as e:

        if conn:
            conn.rollback()

        flash(f'Error al actualizar estado: {e}')

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.asociados')
    )

## Listamos los fundadores
@asesor_bp.route('/fundadores')
def fundadores():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                f.cedula,
                a.nombre,
                a.apellido,
                f.numero_acta,
                f.anio_reconocimiento,
                f.beneficios
            FROM fundador f
            JOIN asociado a
                ON f.cedula = a.cedula
            ORDER BY a.nombre
        """)

        fundadores = cur.fetchall()

        return render_template(
            'fundadores.html',
            fundadores=fundadores
        )

    except Exception as e:

        flash(f'Error al consultar fundadores: {e}')

        return render_template(
            'fundadores.html',
            fundadores=[]
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Formulario nuevo fundador
@asesor_bp.route('/fundadores/nuevo')
def nuevo_fundador():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                a.cedula,
                a.nombre,
                a.apellido
            FROM asociado a
            WHERE NOT EXISTS (
                SELECT 1
                FROM fundador f
                WHERE f.cedula = a.cedula
            )
            ORDER BY a.nombre
        """)

        asociados = cur.fetchall()

        return render_template(
            'nuevo_fundador.html',
            asociados=asociados
        )

    except Exception as e:

        flash(f'Error: {e}')

        return redirect(
            url_for('asesor.fundadores')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Creamos un fundador
@asesor_bp.route(
    '/fundadores/crear',
    methods=['POST']
)
def crear_fundador():

    conn = None
    cur = None

    try:

        cedula = request.form.get('cedula')

        numero_acta = request.form.get(
            'numero_acta'
        )

        anio_reconocimiento = request.form.get(
            'anio_reconocimiento'
        )

        beneficios = request.form.get(
            'beneficios'
        )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO fundador(
                cedula,
                numero_acta,
                anio_reconocimiento,
                beneficios
            )
            VALUES (%s,%s,%s,%s)
        """,
        (
            cedula,
            numero_acta,
            anio_reconocimiento,
            beneficios
        ))

        conn.commit()

        flash(
            'Fundador registrado correctamente'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al registrar fundador: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.fundadores')
    )

## Listamos las atenciones 
@asesor_bp.route('/atenciones')
def atenciones():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                at.cedula_empleado,
                e.nombre,
                e.apellido,
                at.cedula_asociado,
                a.nombre,
                a.apellido,
                at.fecha_atencion
            FROM atiende at
            JOIN empleado e
                ON at.cedula_empleado =
                   e.cedula_emple
            JOIN asociado a
                ON at.cedula_asociado =
                   a.cedula
            ORDER BY at.fecha_atencion DESC
        """)

        atenciones = cur.fetchall()

        return render_template(
            'atenciones.html',
            atenciones=atenciones
        )

    except Exception as e:

        flash(
            f'Error al consultar atenciones: {e}'
        )

        return render_template(
            'atenciones.html',
            atenciones=[]
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()
        
## Formulario nueva atención
@asesor_bp.route('/atenciones/nueva')
def nueva_atencion():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                cedula_emple,
                nombre,
                apellido
            FROM empleado
            ORDER BY nombre
        """)

        empleados = cur.fetchall()

        cur.execute("""
            SELECT
                cedula,
                nombre,
                apellido
            FROM asociado
            ORDER BY nombre
        """)

        asociados = cur.fetchall()

        return render_template(
            'nueva_atencion.html',
            empleados=empleados,
            asociados=asociados
        )

    except Exception as e:

        flash(f'Error: {e}')

        return redirect(
            url_for('asesor.atenciones')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Registramos una atención
@asesor_bp.route(
    '/atenciones/crear',
    methods=['POST']
)
def crear_atencion():

    conn = None
    cur = None

    try:

        cedula_empleado = request.form.get(
            'cedula_empleado'
        )

        cedula_asociado = request.form.get(
            'cedula_asociado'
        )

        fecha_atencion = request.form.get(
            'fecha_atencion'
        )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO atiende(
                cedula_empleado,
                cedula_asociado,
                fecha_atencion
            )
            VALUES (%s,%s,%s)
        """,
        (
            cedula_empleado,
            cedula_asociado,
            fecha_atencion
        ))

        conn.commit()

        flash(
            'Atención registrada correctamente'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al registrar atención: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.atenciones')
    )

## Listamos los beneficiarios
@asesor_bp.route('/beneficiarios')
def beneficiarios():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                b.documento,
                b.nombre,
                b.parentesco,
                b.porcentaje,
                b.telefono,
                a.nombre,
                a.apellido
            FROM beneficiario b
            JOIN asociado a
                ON b.cedula_asociado = a.cedula
            ORDER BY b.nombre
        """)

        beneficiarios = cur.fetchall()

        return render_template(
            'beneficiarios.html',
            beneficiarios=beneficiarios
        )

    except Exception as e:

        flash(f'Error al consultar beneficiarios: {e}')

        return render_template(
            'beneficiarios.html',
            beneficiarios=[]
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


## Formulario nuevo beneficiario
@asesor_bp.route('/beneficiarios/nuevo')
def nuevo_beneficiario():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                cedula,
                nombre,
                apellido
            FROM asociado
            ORDER BY nombre
        """)

        asociados = cur.fetchall()

        return render_template(
            'nuevo_beneficiario.html',
            asociados=asociados
        )

    except Exception as e:

        flash(f'Error: {e}')

        return redirect(
            url_for('asesor.beneficiarios')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Creamos un beneficiario - Restringimos a máximo 4 beneficiarios por asociado y porcentaje acumulado máximo 100%
@asesor_bp.route('/beneficiarios/crear', methods=['POST'])
def crear_beneficiario():

    conn = None
    cur = None

    try:

        documento = request.form.get('documento')
        nombre = request.form.get('nombre')
        parentesco = request.form.get('parentesco')
        porcentaje = float(
            request.form.get('porcentaje')
        )
        telefono = request.form.get('telefono')
        cedula_asociado = request.form.get(
            'cedula_asociado'
        )

        conn = get_connection()
        cur = conn.cursor()

        # Máximo 4 beneficiarios

        cur.execute("""
            SELECT COUNT(*)
            FROM beneficiario
            WHERE cedula_asociado = %s
        """, (cedula_asociado,))

        cantidad = cur.fetchone()[0]

        if cantidad >= 4:

            flash(
                'El asociado ya tiene 4 beneficiarios'
            )

            return redirect(
                url_for(
                    'asesor.nuevo_beneficiario'
                )
            )

        # Validar porcentaje acumulado

        cur.execute("""
            SELECT
                COALESCE(
                    SUM(porcentaje),
                    0
                )
            FROM beneficiario
            WHERE cedula_asociado = %s
        """, (cedula_asociado,))

        porcentaje_actual = cur.fetchone()[0]

        if porcentaje_actual + porcentaje > 100:

            flash(
                'La suma de porcentajes supera el 100%'
            )

            return redirect(
                url_for(
                    'asesor.nuevo_beneficiario'
                )
            )

        cur.execute("""
            INSERT INTO beneficiario(
                documento,
                nombre,
                parentesco,
                porcentaje,
                telefono,
                cedula_asociado
            )
            VALUES (%s,%s,%s,%s,%s,%s)
        """,
        (
            documento,
            nombre,
            parentesco,
            porcentaje,
            telefono,
            cedula_asociado
        ))

        conn.commit()

        flash(
            'Beneficiario registrado correctamente'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al registrar beneficiario: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.beneficiarios')
    )            

## Editamos un beneficiario
@asesor_bp.route('/beneficiarios/editar/<documento>')
def editar_beneficiario(documento):

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
                telefono,
                cedula_asociado
            FROM beneficiario
            WHERE documento = %s
        """, (documento,))

        beneficiario = cur.fetchone()

        if not beneficiario:

            flash('Beneficiario no encontrado')

            return redirect(
                url_for('asesor.beneficiarios')
            )

        cur.execute("""
            SELECT
                cedula,
                nombre,
                apellido
            FROM asociado
            ORDER BY nombre
        """)

        asociados = cur.fetchall()

        return render_template(
            'editar_beneficiario.html',
            beneficiario=beneficiario,
            asociados=asociados
        )

    except Exception as e:

        flash(
            f'Error al cargar beneficiario: {e}'
        )

        return redirect(
            url_for('asesor.beneficiarios')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Actualizamos un beneficiario
@asesor_bp.route(
    '/beneficiarios/actualizar/<documento>',
    methods=['POST']
)
def actualizar_beneficiario(documento):

    conn = None
    cur = None

    try:

        nombre = request.form.get('nombre')
        parentesco = request.form.get('parentesco')
        porcentaje = float(
            request.form.get('porcentaje')
        )
        telefono = request.form.get('telefono')
        cedula_asociado = request.form.get(
            'cedula_asociado'
        )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                COALESCE(
                    SUM(porcentaje),
                    0
                )
            FROM beneficiario
            WHERE cedula_asociado = %s
            AND documento <> %s
        """,
        (
            cedula_asociado,
            documento
        ))

        porcentaje_actual = cur.fetchone()[0]

        if porcentaje_actual + porcentaje > 100:

            flash(
                'La suma de porcentajes supera el 100%'
            )

            return redirect(
                url_for(
                    'asesor.editar_beneficiario',
                    documento=documento
                )
            )

        cur.execute("""
            UPDATE beneficiario
            SET
                nombre = %s,
                parentesco = %s,
                porcentaje = %s,
                telefono = %s,
                cedula_asociado = %s
            WHERE documento = %s
        """,
        (
            nombre,
            parentesco,
            porcentaje,
            telefono,
            cedula_asociado,
            documento
        ))

        conn.commit()

        flash(
            'Beneficiario actualizado correctamente'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al actualizar beneficiario: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.beneficiarios')
    )

## Listamos las cuentas
@asesor_bp.route('/cuentas')
def cuentas():

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
                a.cedula,
                a.nombre,
                a.apellido,
                ag.nombre
            FROM cuenta_ahorro c
            JOIN asociado a
                ON c.cedula_asociado = a.cedula
            JOIN agencia ag
                ON c.codigo_agencia = ag.codigo
            ORDER BY c.numero_cuenta
        """)

        cuentas = cur.fetchall()

        return render_template(
            'cuentas.html',
            cuentas=cuentas
        )

    except Exception as e:

        flash(f'Error al consultar cuentas: {e}')

        return render_template(
            'cuentas.html',
            cuentas=[]
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


## Formulario nueva cuenta
@asesor_bp.route('/cuentas/nueva')
def nueva_cuenta():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                cedula,
                nombre,
                apellido
            FROM asociado
            WHERE estado = 'activo'
            ORDER BY nombre
        """)

        asociados = cur.fetchall()

        cur.execute("""
            SELECT
                codigo,
                nombre
            FROM agencia
            ORDER BY nombre
        """)

        agencias = cur.fetchall()

        return render_template(
            'nueva_cuenta.html',
            asociados=asociados,
            agencias=agencias
        )

    except Exception as e:

        flash(f'Error: {e}')

        return redirect(
            url_for('asesor.cuentas')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Creamos una cuenta
@asesor_bp.route('/cuentas/crear', methods=['POST'])
def crear_cuenta():

    conn = None
    cur = None

    try:

        numero_cuenta = request.form.get(
            'numero_cuenta'
        )

        fecha_apertura = request.form.get(
            'fecha_apertura'
        )

        estado = request.form.get(
            'estado'
        )

        cedula_asociado = request.form.get(
            'cedula_asociado'
        )

        codigo_agencia = request.form.get(
            'codigo_agencia'
        )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO cuenta_ahorro(
                numero_cuenta,
                fecha_apertura,
                estado,
                cedula_asociado,
                codigo_agencia
            )
            VALUES (%s,%s,%s,%s,%s)
        """,
        (
            numero_cuenta,
            fecha_apertura,
            estado,
            cedula_asociado,
            codigo_agencia
        ))

        conn.commit()

        flash(
            'Cuenta creada correctamente'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al crear cuenta: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.cuentas')
    )

## Editamos una cuenta
@asesor_bp.route('/cuentas/editar/<int:numero_cuenta>')
def editar_cuenta(numero_cuenta):

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                numero_cuenta,
                fecha_apertura,
                estado,
                cedula_asociado,
                codigo_agencia
            FROM cuenta_ahorro
            WHERE numero_cuenta = %s
        """, (numero_cuenta,))

        cuenta = cur.fetchone()

        if not cuenta:

            flash('Cuenta no encontrada')

            return redirect(
                url_for('asesor.cuentas')
            )

        cur.execute("""
            SELECT
                cedula,
                nombre,
                apellido
            FROM asociado
            ORDER BY nombre
        """)

        asociados = cur.fetchall()

        cur.execute("""
            SELECT
                codigo,
                nombre
            FROM agencia
            ORDER BY nombre
        """)

        agencias = cur.fetchall()

        return render_template(
            'editar_cuenta.html',
            cuenta=cuenta,
            asociados=asociados,
            agencias=agencias
        )

    except Exception as e:

        flash(f'Error al cargar cuenta: {e}')

        return redirect(
            url_for('asesor.cuentas')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Actualizamos una cuenta
@asesor_bp.route(
    '/cuentas/actualizar/<int:numero_cuenta>',
    methods=['POST']
)
def actualizar_cuenta(numero_cuenta):

    conn = None
    cur = None

    try:

        fecha_apertura = request.form.get(
            'fecha_apertura'
        )

        estado = request.form.get(
            'estado'
        )

        cedula_asociado = request.form.get(
            'cedula_asociado'
        )

        codigo_agencia = request.form.get(
            'codigo_agencia'
        )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE cuenta_ahorro
            SET
                fecha_apertura = %s,
                estado = %s,
                cedula_asociado = %s,
                codigo_agencia = %s
            WHERE numero_cuenta = %s
        """,
        (
            fecha_apertura,
            estado,
            cedula_asociado,
            codigo_agencia,
            numero_cuenta
        ))

        conn.commit()

        flash(
            'Cuenta actualizada correctamente'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al actualizar cuenta: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.cuentas')
    )

## Cambiamos el estado de una cuenta
@asesor_bp.route(
    '/cuentas/cambiar_estado/<int:numero_cuenta>',
    methods=['POST']
)
def cambiar_estado_cuenta(numero_cuenta):

    conn = None
    cur = None

    try:

        nuevo_estado = request.form.get(
            'estado'
        )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE cuenta_ahorro
            SET estado = %s
            WHERE numero_cuenta = %s
        """,
        (
            nuevo_estado,
            numero_cuenta
        ))

        conn.commit()

        flash(
            'Estado actualizado correctamente'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al actualizar estado: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.cuentas')
    )

## Listamos los movimientos
@asesor_bp.route('/movimientos')
def movimientos():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id_transaccion,
                fecha_hora,
                tipo,
                valor,
                canal,
                numero_cuenta,
                cuenta_destino_origen
            FROM movimiento
            ORDER BY fecha_hora DESC
        """)

        movimientos = cur.fetchall()

        return render_template(
            'movimientos.html',
            movimientos=movimientos
        )

    except Exception as e:

        flash(f'Error al consultar movimientos: {e}')

        return render_template(
            'movimientos.html',
            movimientos=[]
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Formulario nuevo movimiento
@asesor_bp.route('/movimientos/nuevo')
def nuevo_movimiento():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                numero_cuenta
            FROM cuenta_ahorro
            WHERE estado = 'activa'
            ORDER BY numero_cuenta
        """)

        cuentas = cur.fetchall()

        return render_template(
            'nuevo_movimiento.html',
            cuentas=cuentas
        )

    except Exception as e:

        flash(f'Error: {e}')

        return redirect(
            url_for('asesor.movimientos')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Creamos un movimiento
@asesor_bp.route(
    '/movimientos/crear',
    methods=['POST']
)
def crear_movimiento():

    conn = None
    cur = None

    try:

        id_transaccion = request.form.get(
            'id_transaccion'
        )

        fecha_hora = request.form.get(
            'fecha_hora'
        )

        tipo = request.form.get(
            'tipo'
        )

        valor = request.form.get(
            'valor'
        )

        if float(valor) <= 0:

            flash(
                'El valor del movimiento debe ser mayor a cero'
            )

            return redirect(
                url_for('asesor.nuevo_movimiento')
            )

        canal = request.form.get(
            'canal'
        )

        numero_cuenta = request.form.get(
            'numero_cuenta'
        )

        cuenta_destino_origen = request.form.get(
            'cuenta_destino_origen'
        ) or None

        if (
            'transferencia' in tipo.lower()
            and not cuenta_destino_origen
        ):
            flash(
                'La cuenta destino/origen es obligatoria para transferencias'
            )

            return redirect(
                url_for('asesor.nuevo_movimiento')
            )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO movimiento(
                id_transaccion,
                fecha_hora,
                tipo,
                valor,
                canal,
                numero_cuenta,
                cuenta_destino_origen
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            id_transaccion,
            fecha_hora,
            tipo,
            valor,
            canal,
            numero_cuenta,
            cuenta_destino_origen
        ))

        conn.commit()

        flash(
            'Movimiento registrado correctamente'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al registrar movimiento: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.movimientos')
    )

## Listamos los créditos
@asesor_bp.route('/creditos')
def creditos():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                c.numero_radicado,
                c.valor_solicitado,
                c.valor_aprobado,
                c.plazo,
                c.tasa_interes,
                c.linea_credito,
                c.estado,
                a.nombre,
                a.apellido,
                ag.nombre
            FROM credito c
            JOIN asociado a
                ON c.cedula_asociado = a.cedula
            JOIN agencia ag
                ON c.codigo_agencia = ag.codigo
            ORDER BY c.numero_radicado
        """)

        creditos = cur.fetchall()

        return render_template(
            'creditos.html',
            creditos=creditos
        )

    except Exception as e:

        flash(f'Error al consultar créditos: {e}')

        return render_template(
            'creditos.html',
            creditos=[]
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Formulario nuevo crédito
@asesor_bp.route('/creditos/nuevo')
def nuevo_credito():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                cedula,
                nombre,
                apellido
            FROM asociado
            WHERE estado = 'activo'
            ORDER BY nombre
        """)

        asociados = cur.fetchall()

        cur.execute("""
            SELECT
                codigo,
                nombre
            FROM agencia
            ORDER BY nombre
        """)

        agencias = cur.fetchall()

        return render_template(
            'nuevo_credito.html',
            asociados=asociados,
            agencias=agencias
        )

    except Exception as e:

        flash(f'Error: {e}')

        return redirect(
            url_for('asesor.creditos')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


## Creamos un crédito
@asesor_bp.route('/creditos/crear', methods=['POST'])
def crear_credito():

    conn = None
    cur = None

    try:

        numero_radicado = request.form.get(
            'numero_radicado'
        )

        valor_solicitado = request.form.get(
            'valor_solicitado'
        )

        valor_aprobado = request.form.get(
            'valor_aprobado'
        )

        plazo = request.form.get(
            'plazo'
        )

        tasa_interes = request.form.get(
            'tasa_interes'
        )

        fecha_aprobacion = request.form.get(
            'fecha_aprobacion'
        )

        fecha_primer_vencimiento = request.form.get(
            'fecha_primer_vencimiento'
        )

        linea_credito = request.form.get(
            'linea_credito'
        )

        estado = request.form.get(
            'estado'
        )

        cedula_asociado = request.form.get(
            'cedula_asociado'
        )

        codigo_agencia = request.form.get(
            'codigo_agencia'
        )

        if float(valor_aprobado) > float(valor_solicitado):

            flash(
                'El valor aprobado no puede ser mayor al valor solicitado'
            )

            return redirect(
                url_for('asesor.nuevo_credito')
            )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO credito(
                numero_radicado,
                valor_solicitado,
                valor_aprobado,
                plazo,
                tasa_interes,
                fecha_aprobacion,
                fecha_primer_vencimiento,
                linea_credito,
                estado,
                cedula_asociado,
                codigo_agencia
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            numero_radicado,
            valor_solicitado,
            valor_aprobado,
            plazo,
            tasa_interes,
            fecha_aprobacion,
            fecha_primer_vencimiento,
            linea_credito,
            estado,
            cedula_asociado,
            codigo_agencia
        ))

        conn.commit()

        flash(
            'Crédito registrado correctamente'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al registrar crédito: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.creditos')
    )

## Editamos un crédito
@asesor_bp.route('/creditos/editar/<int:numero_radicado>')
def editar_credito(numero_radicado):

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM credito
            WHERE numero_radicado = %s
        """, (numero_radicado,))

        credito = cur.fetchone()

        if not credito:

            flash('Crédito no encontrado')

            return redirect(
                url_for('asesor.creditos')
            )

        cur.execute("""
            SELECT cedula, nombre, apellido
            FROM asociado
            ORDER BY nombre
        """)

        asociados = cur.fetchall()

        cur.execute("""
            SELECT codigo, nombre
            FROM agencia
            ORDER BY nombre
        """)

        agencias = cur.fetchall()

        return render_template(
            'editar_credito.html',
            credito=credito,
            asociados=asociados,
            agencias=agencias
        )

    except Exception as e:

        flash(
            f'Error al cargar crédito: {e}'
        )

        return redirect(
            url_for('asesor.creditos')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Actualizamos un crédito
@asesor_bp.route(
    '/creditos/actualizar/<int:numero_radicado>',
    methods=['POST']
)
def actualizar_credito(numero_radicado):

    conn = None
    cur = None

    try:

        valor_solicitado = request.form.get(
            'valor_solicitado'
        )

        valor_aprobado = request.form.get(
            'valor_aprobado'
        )

        plazo = request.form.get(
            'plazo'
        )

        tasa_interes = request.form.get(
            'tasa_interes'
        )

        fecha_aprobacion = request.form.get(
            'fecha_aprobacion'
        )

        fecha_primer_vencimiento = request.form.get(
            'fecha_primer_vencimiento'
        )

        linea_credito = request.form.get(
            'linea_credito'
        )

        estado = request.form.get(
            'estado'
        )

        cedula_asociado = request.form.get(
            'cedula_asociado'
        )

        codigo_agencia = request.form.get(
            'codigo_agencia'
        )

        if float(valor_aprobado) > float(valor_solicitado):

            flash(
                'El valor aprobado no puede ser mayor al valor solicitado'
            )

            return redirect(
                url_for(
                    'asesor.editar_credito',
                    numero_radicado=numero_radicado
                )
            )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE credito
            SET
                valor_solicitado = %s,
                valor_aprobado = %s,
                plazo = %s,
                tasa_interes = %s,
                fecha_aprobacion = %s,
                fecha_primer_vencimiento = %s,
                linea_credito = %s,
                estado = %s,
                cedula_asociado = %s,
                codigo_agencia = %s
            WHERE numero_radicado = %s
        """,
        (
            valor_solicitado,
            valor_aprobado,
            plazo,
            tasa_interes,
            fecha_aprobacion,
            fecha_primer_vencimiento,
            linea_credito,
            estado,
            cedula_asociado,
            codigo_agencia,
            numero_radicado
        ))

        conn.commit()

        flash(
            'Crédito actualizado correctamente'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al actualizar crédito: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.creditos')
    )
    

## Cambiamos el estado de un crédito
@asesor_bp.route(
    '/creditos/cambiar_estado/<int:numero_radicado>',
    methods=['POST']
)
def cambiar_estado_credito(numero_radicado):

    conn = None
    cur = None

    try:

        nuevo_estado = request.form.get('estado')

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE credito
            SET estado = %s
            WHERE numero_radicado = %s
        """,
        (
            nuevo_estado,
            numero_radicado
        ))

        conn.commit()

        flash(
            'Estado actualizado correctamente'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al actualizar estado: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.creditos')
    )

## Listamos los codeudores
@asesor_bp.route('/codeudores')
def codeudores():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                c.numero_radicado,
                c.cedula_codeudor,
                a.nombre,
                a.apellido,
                c.fecha_firma
            FROM codeudor c
            JOIN asociado a
                ON c.cedula_codeudor = a.cedula
            ORDER BY c.numero_radicado
        """)

        codeudores = cur.fetchall()

        return render_template(
            'codeudores.html',
            codeudores=codeudores
        )

    except Exception as e:

        flash(f'Error al consultar codeudores: {e}')

        return render_template(
            'codeudores.html',
            codeudores=[]
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Formulario nuevo codeudor
@asesor_bp.route('/codeudores/nuevo')
def nuevo_codeudor():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                numero_radicado
            FROM credito
            ORDER BY numero_radicado
        """)

        creditos = cur.fetchall()

        cur.execute("""
            SELECT
                cedula,
                nombre,
                apellido
            FROM asociado
            WHERE estado = 'activo'
            ORDER BY nombre
        """)

        asociados = cur.fetchall()

        return render_template(
            'nuevo_codeudor.html',
            creditos=creditos,
            asociados=asociados
        )

    except Exception as e:

        flash(f'Error: {e}')

        return redirect(
            url_for('asesor.codeudores')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Creamos un codeudor
@asesor_bp.route(
    '/codeudores/crear',
    methods=['POST']
)
def crear_codeudor():

    conn = None
    cur = None

    try:

        numero_radicado = request.form.get(
            'numero_radicado'
        )

        cedula_codeudor = request.form.get(
            'cedula_codeudor'
        )

        fecha_firma = request.form.get(
            'fecha_firma'
        )

        conn = get_connection()
        cur = conn.cursor()

        # Validación
        cur.execute("""
            SELECT COUNT(*)
            FROM codeudor
            WHERE numero_radicado = %s
              AND cedula_codeudor = %s
        """, (numero_radicado, cedula_codeudor))

        existe = cur.fetchone()[0]

        if existe > 0:

            flash(
                'El codeudor ya está registrado para este crédito'
            )

            return redirect(
                url_for('asesor.nuevo_codeudor')
            )

        cur.execute("""
            INSERT INTO codeudor(
                numero_radicado,
                cedula_codeudor,
                fecha_firma
            )
            VALUES (%s,%s,%s)
        """,
        (
            numero_radicado,
            cedula_codeudor,
            fecha_firma
        ))

        conn.commit()

        flash(
            'Codeudor registrado correctamente'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al registrar codeudor: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.codeudores')
    )

## Listamos los pagos
@asesor_bp.route('/pagos')
def pagos():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                numero_radicado,
                numero_cuota,
                fecha_pago,
                valor_pagado,
                estado
            FROM pago_cuota
            ORDER BY numero_radicado,
                     numero_cuota
        """)

        pagos = cur.fetchall()

        return render_template(
            'pagos.html',
            pagos=pagos
        )

    except Exception as e:

        flash(
            f'Error al consultar pagos: {e}'
        )

        return render_template(
            'pagos.html',
            pagos=[]
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Formulario nuevo pago
@asesor_bp.route('/pagos/nuevo')
def nuevo_pago():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                numero_radicado
            FROM credito
            ORDER BY numero_radicado
        """)

        creditos = cur.fetchall()

        return render_template(
            'nuevo_pago.html',
            creditos=creditos
        )

    except Exception as e:

        flash(f'Error: {e}')

        return redirect(
            url_for('asesor.pagos')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Creamos un pago
@asesor_bp.route(
    '/pagos/crear',
    methods=['POST']
)
def crear_pago():

    conn = None
    cur = None

    try:

        numero_radicado = request.form.get(
            'numero_radicado'
        )

        numero_cuota = request.form.get(
            'numero_cuota'
        )

        fecha_pago = request.form.get(
            'fecha_pago'
        )

        valor_pagado = request.form.get(
            'valor_pagado'
        )

        estado = request.form.get(
            'estado'
        )

        # Validación
        if float(valor_pagado) <= 0:

            flash(
                'El valor pagado debe ser mayor a cero'
            )

            return redirect(
                url_for('asesor.nuevo_pago')
            )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO pago_cuota(
                numero_radicado,
                numero_cuota,
                fecha_pago,
                valor_pagado,
                estado
            )
            VALUES (%s,%s,%s,%s,%s)
        """,
        (
            numero_radicado,
            numero_cuota,
            fecha_pago,
            valor_pagado,
            estado
        ))

        conn.commit()

        flash(
            'Pago registrado correctamente'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        flash(
            f'Error al registrar pago: {e}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('asesor.pagos')
    )