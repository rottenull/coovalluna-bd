from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_connection
from utils.bitacora import registrar_bitacora

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')

        if not usuario or not contrasena:
            flash('Debes completar usuario y contraseña')
            return render_template('login.html')

        conn = None
        cur = None

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    usuario,
                    contrasena,
                    rol,
                    estado,
                    cedula_empleado,
                    cedula_asociado
                FROM usuario_sistema
                WHERE usuario = %s
            """, (usuario,))

            cuenta = cur.fetchone()

            if not cuenta:
                flash('Usuario no encontrado')
                return render_template('login.html')

            usuario_db = cuenta[0]
            contrasena_db = cuenta[1]
            rol = cuenta[2]
            estado = cuenta[3]
            cedula_empleado = cuenta[4]
            cedula_asociado = cuenta[5]

            if estado != 'activo':
                flash('La cuenta está inactiva')
                return render_template('login.html')

            if contrasena != contrasena_db:
                flash('Contraseña incorrecta')
                return render_template('login.html')

            session.clear()
            session['usuario'] = usuario_db
            session['rol'] = rol
            session['cedula_empleado'] = cedula_empleado
            session['cedula_asociado'] = cedula_asociado

            registrar_bitacora(usuario_db, f'Inicio de sesión ({rol})')

            if rol == 'admin':
                return redirect(url_for('auth.dashboard_admin'))
            elif rol == 'asesor':
                return redirect(url_for('auth.dashboard_asesor'))
            elif rol == 'asociado':
                return redirect(url_for('auth.dashboard_asociado'))
            else:
                flash('Rol no válido')
                return render_template('login.html')

        except Exception as e:
            flash(f'Error al iniciar sesión: {e}')
            return render_template('login.html')

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    usuario = session.get('usuario')

    if usuario:
        registrar_bitacora(usuario, 'Cierre de sesión')

    session.clear()
    flash('Sesión cerrada correctamente')
    return redirect(url_for('auth.login'))


@auth_bp.route('/dashboard/admin')
def dashboard_admin():
    if session.get('rol') != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('auth.login'))

    return render_template('dashboard_admin.html')


@auth_bp.route('/dashboard/asesor')
def dashboard_asesor():
    if session.get('rol') != 'asesor':
        flash('Acceso no autorizado')
        return redirect(url_for('auth.login'))

    return render_template('dashboard_asesor.html')


@auth_bp.route('/dashboard/asociado')
def dashboard_asociado():
    if session.get('rol') != 'asociado':
        flash('Acceso no autorizado')
        return redirect(url_for('auth.login'))

    return render_template('dashboard_asociado.html')