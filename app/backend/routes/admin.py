from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection

admin_bp = Blueprint('admin', __name__)

## Consultar bitácora de auditoría
@admin_bp.route('/auditoria')
def auditoria():

    conn = None
    cur = None

    try:

        usuario = request.args.get('usuario')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')

        conn = get_connection()
        cur = conn.cursor()

        consulta = """
            SELECT
                id_registro,
                fecha_hora,
                usuario,
                operacion
            FROM bitacora
            WHERE 1 = 1
        """

        parametros = []

        if usuario:
            consulta += """
                AND usuario = %s
            """
            parametros.append(usuario)

        if fecha_desde:
            consulta += """
                AND fecha_hora >= %s
            """
            parametros.append(fecha_desde)

        if fecha_hasta:
            consulta += """
                AND fecha_hora <= %s
            """
            parametros.append(fecha_hasta)

        consulta += """
            ORDER BY fecha_hora DESC
        """

        cur.execute(
            consulta,
            tuple(parametros)
        )

        registros = cur.fetchall()

        return render_template(
            'auditoria.html',
            registros=registros
        )

    except Exception as e:

        flash(
            f'Error al consultar auditoría: {e}'
        )

        return redirect(
            url_for('auth.dashboard_admin')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Listamos las agencias 
@admin_bp.route('/agencias')
def agencias():

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT codigo, nombre, direccion,
                   municipio, telefono, fecha_apertura
            FROM agencia
            ORDER BY nombre
        """)

        agencias = cur.fetchall()

        return render_template(
            'agencias.html',
            agencias=agencias
        )

    except Exception as e:
        flash(f'Error al consultar agencias: {e}')
        return render_template('agencias.html', agencias=[])

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()


## Formulario nueva agencia
@admin_bp.route('/agencias/nueva')
def nueva_agencia():

    return render_template(
        'nueva_agencia.html'
    )


## Creamos una nueva agencia
@admin_bp.route('/agencias/crear', methods=['POST'])
def crear_agencia():

    conn = None
    cur = None

    try:

        codigo = request.form.get('codigo')
        nombre = request.form.get('nombre')
        direccion = request.form.get('direccion')
        municipio = request.form.get('municipio')
        telefono = request.form.get('telefono')
        fecha_apertura = request.form.get('fecha_apertura')

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO agencia(
                codigo,
                nombre,
                direccion,
                municipio,
                telefono,
                fecha_apertura
            )
            VALUES (%s,%s,%s,%s,%s,%s)
        """,
        (
            codigo,
            nombre,
            direccion,
            municipio,
            telefono,
            fecha_apertura
        ))

        conn.commit()

        flash('Agencia creada correctamente')

    except Exception as e:

        if conn:
            conn.rollback()

        flash(f'Error al crear agencia: {e}')

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(url_for('admin.agencias'))


## Editamos una agencia
@admin_bp.route('/agencias/editar/<int:codigo>')
def editar_agencia(codigo):

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT codigo,
                   nombre,
                   direccion,
                   municipio,
                   telefono,
                   fecha_apertura
            FROM agencia
            WHERE codigo = %s
        """, (codigo,))

        agencia = cur.fetchone()

        if not agencia:
            flash('Agencia no encontrada')
            return redirect(url_for('admin.agencias'))
        
        return render_template(
            'editar_agencia.html',
            agencia=agencia
        )

    except Exception as e:
        flash(f'Error: {e}')
        return redirect(url_for('admin.agencias'))

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()

## Actualizamos una agencia
@admin_bp.route('/agencias/actualizar/<int:codigo>', methods=['POST'])
def actualizar_agencia(codigo):

    conn = None
    cur = None

    try:

        nombre = request.form.get('nombre')
        direccion = request.form.get('direccion')
        municipio = request.form.get('municipio')
        telefono = request.form.get('telefono')
        fecha_apertura = request.form.get('fecha_apertura')

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE agencia
            SET nombre = %s,
                direccion = %s,
                municipio = %s,
                telefono = %s,
                fecha_apertura = %s
            WHERE codigo = %s
        """,
        (
            nombre,
            direccion,
            municipio,
            telefono,
            fecha_apertura,
            codigo
        ))

        conn.commit()

        flash('Agencia actualizada correctamente')

    except Exception as e:

        if conn:
            conn.rollback()

        flash(f'Error al actualizar: {e}')

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(url_for('admin.agencias'))


## Listamos los empleados
@admin_bp.route('/empleados')
def empleados():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                e.cedula_emple,
                e.nombre,
                e.apellido,
                c.nombre_cargo,
                a.nombre,
                e.estado
            FROM empleado e
            JOIN cargo c
                ON e.id_cargo = c.id_cargo
            JOIN agencia a
                ON e.codigo_agencia = a.codigo
            ORDER BY e.nombre
        """)

        empleados = cur.fetchall()

        return render_template(
            'empleados.html',
            empleados=empleados
        )

    except Exception as e:

        flash(f'Error al consultar empleados: {e}')

        return render_template(
            'empleados.html',
            empleados=[]
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Formulario nuevo empleado
@admin_bp.route('/empleados/nuevo')
def nuevo_empleado():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT codigo, nombre
            FROM agencia
            ORDER BY nombre
        """)
        agencias = cur.fetchall()

        cur.execute("""
            SELECT id_cargo, nombre_cargo
            FROM cargo
            ORDER BY nombre_cargo
        """)
        cargos = cur.fetchall()

        cur.execute("""
            SELECT
                cedula_emple,
                nombre,
                apellido
            FROM empleado
            ORDER BY nombre
        """)
        supervisores = cur.fetchall()

        return render_template(
            'nuevo_empleado.html',
            agencias=agencias,
            cargos=cargos,
            supervisores=supervisores
        )

    except Exception as e:

        flash(f'Error: {e}')

        return redirect(url_for('admin.empleados'))

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Creamos un nuevo empleado
@admin_bp.route('/empleados/crear', methods=['POST'])
def crear_empleado():

    conn = None
    cur = None

    try:

        cedula = request.form.get('cedula_emple')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        fecha_ingreso = request.form.get('fecha_ingreso')
        salario = request.form.get('salario')
        correo = request.form.get('correo')
        estado = request.form.get('estado')
        codigo_agencia = request.form.get('codigo_agencia')
        id_cargo = request.form.get('id_cargo')

        supervisor = request.form.get('supervisor_cedula') or None

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO empleado(
                cedula_emple,
                nombre,
                apellido,
                fecha_ingreso,
                salario,
                correo,
                estado,
                codigo_agencia,
                id_cargo,
                supervisor_cedula
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            cedula,
            nombre,
            apellido,
            fecha_ingreso,
            salario,
            correo,
            estado,
            codigo_agencia,
            id_cargo,
            supervisor
        ))

        conn.commit()

        flash('Empleado registrado correctamente')

    except Exception as e:

        if conn:
            conn.rollback()

        flash(f'Error al registrar empleado: {e}')

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(url_for('admin.empleados'))

## Editamos un empleado
@admin_bp.route('/empleados/editar/<cedula>')
def editar_empleado(cedula):

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        # Buscar empleado
        cur.execute("""
            SELECT
                cedula_emple,
                nombre,
                apellido,
                fecha_ingreso,
                salario,
                correo,
                estado,
                codigo_agencia,
                id_cargo,
                supervisor_cedula
            FROM empleado
            WHERE cedula_emple = %s
        """, (cedula,))

        empleado = cur.fetchone()

        if not empleado:
            flash('Empleado no encontrado')
            return redirect(url_for('admin.empleados'))

        # Agencias
        cur.execute("""
            SELECT codigo, nombre
            FROM agencia
            ORDER BY nombre
        """)
        agencias = cur.fetchall()

        # Cargos
        cur.execute("""
            SELECT id_cargo, nombre_cargo
            FROM cargo
            ORDER BY nombre_cargo
        """)
        cargos = cur.fetchall()

        # Supervisores
        cur.execute("""
            SELECT
                cedula_emple,
                nombre,
                apellido
            FROM empleado
            WHERE cedula_emple <> %s
            ORDER BY nombre
        """, (cedula,))
        supervisores = cur.fetchall()

        return render_template(
            'editar_empleado.html',
            empleado=empleado,
            agencias=agencias,
            cargos=cargos,
            supervisores=supervisores
        )
    
    except Exception as e:

        flash(f'Error al cargar empleado: {e}')

        return redirect(url_for('admin.empleados'))

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


## Actualizamos un empleado
@admin_bp.route('/empleados/actualizar/<cedula>', methods=['POST'])
def actualizar_empleado(cedula):

    conn = None
    cur = None

    try:

        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        fecha_ingreso = request.form.get('fecha_ingreso')
        salario = request.form.get('salario')
        correo = request.form.get('correo')
        estado = request.form.get('estado')
        codigo_agencia = request.form.get('codigo_agencia')
        id_cargo = request.form.get('id_cargo')

        supervisor = request.form.get('supervisor_cedula') or None

        if supervisor == cedula:
            flash('Un empleado no puede ser supervisor de sí mismo')
            return redirect(
                url_for(
                    'admin.editar_empleado',
                    cedula=cedula
                )
            )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE empleado
            SET
                nombre = %s,
                apellido = %s,
                fecha_ingreso = %s,
                salario = %s,
                correo = %s,
                estado = %s,
                codigo_agencia = %s,
                id_cargo = %s,
                supervisor_cedula = %s
            WHERE cedula_emple = %s
        """,
        (
            nombre,
            apellido,
            fecha_ingreso,
            salario,
            correo,
            estado,
            codigo_agencia,
            id_cargo,
            supervisor,
            cedula
        ))

        conn.commit()

        flash('Empleado actualizado correctamente')

    except Exception as e:

        if conn:
            conn.rollback()

        flash(f'Error al actualizar empleado: {e}')

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(url_for('admin.empleados'))

## Cambiamos el estado de un empleado
@admin_bp.route('/empleados/cambiar_estado/<cedula>', methods=['POST'])
def cambiar_estado_empleado(cedula):

    conn = None
    cur = None

    try:

        nuevo_estado = request.form.get('estado')

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE empleado
            SET estado = %s
            WHERE cedula_emple = %s
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
        url_for('admin.empleados')
    )

## 11