from flask import Blueprint, render_template, request, redirect, url_for, flash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        rol = request.form.get('rol')

        if not usuario or not rol:
            flash('debes completar los campos requeridos')
            return render_template('login.html')

        if rol == 'admin':
            return redirect(url_for('auth.dashboard_admin'))
        elif rol == 'asesor':
            return redirect(url_for('auth.dashboard_asesor'))
        elif rol == 'asociado':
            return redirect(url_for('auth.dashboard_asociado'))

        flash('rol no válido')
        return render_template('login.html')

    return render_template('login.html')

@auth_bp.route('/dashboard/admin')
def dashboard_admin():
    return render_template('dashboard_admin.html')
@auth_bp.route('/dashboard/asesor')
def dashboard_asesor():
    return '<h1>dashboard asesor</h1>'

@auth_bp.route('/dashboard/asociado')
def dashboard_asociado():
    return '<h1>dashboard asociado</h1>'