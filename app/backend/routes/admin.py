from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_connection
from utils.bitacora import registrar_bitacora

admin_bp = Blueprint('admin', __name__)

def verificar_admin():
    if session.get('rol') != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('auth.login'))
    return None

## Consultar bitácora de auditoría
@admin_bp.route('/auditoria')
def auditoria():

    control = verificar_admin()
    if control:
        return control

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

    control = verificar_admin()
    if control:
        return control

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

    control = verificar_admin()
    if control:
        return control

    return render_template(
        'nueva_agencia.html'
    )


## Creamos una nueva agencia
@admin_bp.route('/agencias/crear', methods=['POST'])
def crear_agencia():

    control = verificar_admin()
    if control:
        return control

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

        registrar_bitacora(
            session.get('usuario'),
            f'Creó agencia: {nombre} (Código: {codigo})'
        )

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

    control = verificar_admin()
    if control:
        return control

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

    control = verificar_admin()
    if control:
        return control

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

        registrar_bitacora(
            session.get('usuario'),
            f'Actualizó agencia: {nombre} (Código: {codigo})'
        )

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

    control = verificar_admin()
    if control:
        return control

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

    control = verificar_admin()
    if control:
        return control

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

    control = verificar_admin()
    if control:
        return control

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

        registrar_bitacora(
            session.get('usuario'),
            f'Creó empleado {cedula}'
        )

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

    control = verificar_admin()
    if control:
        return control

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

    control = verificar_admin()
    if control:
        return control

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

        registrar_bitacora(
            session.get('usuario'),
            f'Actualizó empleado {cedula}'
        )

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

    control = verificar_admin()
    if control:
        return control

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

## Listamos usuarios y roles
@admin_bp.route('/usuarios')
def usuarios():

    control = verificar_admin()
    if control:
        return control

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id_usuario,
                usuario,
                rol,
                estado,
                cedula_empleado,
                cedula_asociado
            FROM usuario_sistema
            ORDER BY usuario
        """)

        usuarios = cur.fetchall()

        return render_template(
            'usuarios.html',
            usuarios=usuarios
        )

    except Exception as e:
        flash(f'Error al consultar usuarios: {e}')
        return render_template(
            'usuarios.html',
            usuarios=[]
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


## Formulario nuevo usuario
@admin_bp.route('/usuarios/nuevo')
def nuevo_usuario():

    control = verificar_admin()
    if control:
        return control

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
            ORDER BY nombre, apellido
        """)
        empleados = cur.fetchall()

        cur.execute("""
            SELECT
                cedula,
                nombre,
                apellido
            FROM asociado
            ORDER BY nombre, apellido
        """)
        asociados = cur.fetchall()

        return render_template(
            'nuevo_usuario.html',
            empleados=empleados,
            asociados=asociados
        )

    except Exception as e:
        flash(f'Error al cargar formulario: {e}')
        return redirect(url_for('admin.usuarios'))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


## Creamos un nuevo usuario
@admin_bp.route('/usuarios/crear', methods=['POST'])
def crear_usuario():

    control = verificar_admin()
    if control:
        return control

    conn = None
    cur = None

    try:
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        rol = request.form.get('rol')
        estado = request.form.get('estado')
        cedula_empleado = request.form.get('cedula_empleado') or None
        cedula_asociado = request.form.get('cedula_asociado') or None

        if not usuario or not contrasena or not rol or not estado:
            flash('Debes completar los campos obligatorios')
            return redirect(url_for('admin.nuevo_usuario'))

        if rol in ['admin', 'asesor']:
            if not cedula_empleado:
                flash('Para rol admin o asesor debes seleccionar un empleado')
                return redirect(url_for('admin.nuevo_usuario'))
            cedula_asociado = None

        elif rol == 'asociado':
            if not cedula_asociado:
                flash('Para rol asociado debes seleccionar un asociado')
                return redirect(url_for('admin.nuevo_usuario'))
            cedula_empleado = None

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO usuario_sistema (
                usuario,
                contrasena,
                rol,
                estado,
                cedula_empleado,
                cedula_asociado
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            usuario,
            contrasena,
            rol,
            estado,
            cedula_empleado,
            cedula_asociado
        ))

        conn.commit()

        if session.get('usuario'):
            registrar_bitacora(
                session.get('usuario'),
                f'Creó usuario del sistema: {usuario} ({rol})'
            )

        flash('Usuario creado correctamente')

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f'Error al crear usuario: {e}')

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return redirect(url_for('admin.usuarios'))

## Formulario editar usuario
@admin_bp.route('/usuarios/editar/<int:id_usuario>')
def editar_usuario(id_usuario):

    control = verificar_admin()
    if control:
        return control

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id_usuario,
                usuario,
                rol,
                estado,
                cedula_empleado,
                cedula_asociado
            FROM usuario_sistema
            WHERE id_usuario = %s
        """, (id_usuario,))

        usuario = cur.fetchone()

        if not usuario:
            flash('Usuario no encontrado')
            return redirect(url_for('admin.usuarios'))

        cur.execute("""
            SELECT
                cedula_emple,
                nombre,
                apellido
            FROM empleado
            ORDER BY nombre, apellido
        """)
        empleados = cur.fetchall()

        cur.execute("""
            SELECT
                cedula,
                nombre,
                apellido
            FROM asociado
            ORDER BY nombre, apellido
        """)
        asociados = cur.fetchall()

        return render_template(
            'editar_usuario.html',
            usuario=usuario,
            empleados=empleados,
            asociados=asociados
        )

    except Exception as e:
        flash(f'Error al cargar usuario: {e}')
        return redirect(url_for('admin.usuarios'))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


## Actualizar rol y estado de usuario
@admin_bp.route('/usuarios/actualizar/<int:id_usuario>', methods=['POST'])
def actualizar_usuario(id_usuario):

    control = verificar_admin()
    if control:
        return control

    conn = None
    cur = None

    try:
        rol = request.form.get('rol')
        estado = request.form.get('estado')
        cedula_empleado = request.form.get('cedula_empleado') or None
        cedula_asociado = request.form.get('cedula_asociado') or None

        if not rol or not estado:
            flash('Debes completar rol y estado')
            return redirect(url_for('admin.editar_usuario', id_usuario=id_usuario))

        if rol in ['admin', 'asesor']:
            if not cedula_empleado:
                flash('Para rol admin o asesor debes seleccionar un empleado')
                return redirect(url_for('admin.editar_usuario', id_usuario=id_usuario))
            cedula_asociado = None

        elif rol == 'asociado':
            if not cedula_asociado:
                flash('Para rol asociado debes seleccionar un asociado')
                return redirect(url_for('admin.editar_usuario', id_usuario=id_usuario))
            cedula_empleado = None

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE usuario_sistema
            SET
                rol = %s,
                estado = %s,
                cedula_empleado = %s,
                cedula_asociado = %s
            WHERE id_usuario = %s
        """, (
            rol,
            estado,
            cedula_empleado,
            cedula_asociado,
            id_usuario
        ))

        conn.commit()

        flash('Usuario actualizado correctamente')

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f'Error al actualizar usuario: {e}')

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return redirect(url_for('admin.usuarios'))


## Restablecer contraseña
@admin_bp.route('/usuarios/restablecer_contrasena/<int:id_usuario>', methods=['POST'])
def restablecer_contrasena(id_usuario):

    control = verificar_admin()
    if control:
        return control

    conn = None
    cur = None

    try:
        nueva_contrasena = request.form.get('nueva_contrasena')

        if not nueva_contrasena:
            flash('Debes escribir una nueva contraseña')
            return redirect(url_for('admin.editar_usuario', id_usuario=id_usuario))

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE usuario_sistema
            SET contrasena = %s
            WHERE id_usuario = %s
        """, (
            nueva_contrasena,
            id_usuario
        ))

        conn.commit()

        flash('Contraseña restablecida correctamente')

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f'Error al restablecer contraseña: {e}')

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return redirect(url_for('admin.editar_usuario', id_usuario=id_usuario))

## Listamos los cargos
@admin_bp.route('/cargos')
def cargos():

    control = verificar_admin()
    if control:
        return control

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id_cargo,
                nombre_cargo,
                turno,
                zona,
                descripcion
            FROM cargo
            ORDER BY nombre_cargo
        """)

        cargos = cur.fetchall()

        return render_template(
            'cargos.html',
            cargos=cargos
        )

    except Exception as e:

        flash(f'Error al consultar cargos: {e}')

        return render_template(
            'cargos.html',
            cargos=[]
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Formulario nuevo cargo
@admin_bp.route('/cargos/nuevo')
def nuevo_cargo():

    control = verificar_admin()
    if control:
        return control

    return render_template(
        'nuevo_cargo.html'
    )

## Creamos un cargo
@admin_bp.route('/cargos/crear', methods=['POST'])
def crear_cargo():

    control = verificar_admin()
    if control:
        return control

    conn = None
    cur = None

    try:

        id_cargo = request.form.get('id_cargo')
        nombre_cargo = request.form.get('nombre_cargo')
        turno = request.form.get('turno')
        zona = request.form.get('zona')
        descripcion = request.form.get('descripcion')

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO cargo(
                id_cargo,
                nombre_cargo,
                turno,
                zona,
                descripcion
            )
            VALUES (%s,%s,%s,%s,%s)
        """,
        (
            id_cargo,
            nombre_cargo,
            turno,
            zona,
            descripcion
        ))

        conn.commit()

        flash('Cargo creado correctamente')

    except Exception as e:

        if conn:
            conn.rollback()

        flash(f'Error al crear cargo: {e}')

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('admin.cargos')
    )

## Editar cargo
@admin_bp.route('/cargos/editar/<int:id_cargo>')
def editar_cargo(id_cargo):

    control = verificar_admin()
    if control:
        return control

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id_cargo,
                nombre_cargo,
                turno,
                zona,
                descripcion
            FROM cargo
            WHERE id_cargo = %s
        """, (id_cargo,))

        cargo = cur.fetchone()

        if not cargo:

            flash('Cargo no encontrado')

            return redirect(
                url_for('admin.cargos')
            )

        return render_template(
            'editar_cargo.html',
            cargo=cargo
        )

    except Exception as e:

        flash(f'Error al cargar cargo: {e}')

        return redirect(
            url_for('admin.cargos')
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

## Actualizamos un cargo
@admin_bp.route('/cargos/actualizar/<int:id_cargo>', methods=['POST'])
def actualizar_cargo(id_cargo):

    control = verificar_admin()
    if control:
        return control

    conn = None
    cur = None

    try:

        nombre_cargo = request.form.get('nombre_cargo')
        turno = request.form.get('turno')
        zona = request.form.get('zona')
        descripcion = request.form.get('descripcion')

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE cargo
            SET
                nombre_cargo = %s,
                turno = %s,
                zona = %s,
                descripcion = %s
            WHERE id_cargo = %s
        """,
        (
            nombre_cargo,
            turno,
            zona,
            descripcion,
            id_cargo
        ))

        conn.commit()

        flash('Cargo actualizado correctamente')

    except Exception as e:

        if conn:
            conn.rollback()

        flash(f'Error al actualizar cargo: {e}')

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

    return redirect(
        url_for('admin.cargos')
    )