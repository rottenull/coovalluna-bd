from flask import Blueprint, render_template

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/agencias')
def agencias():
    return render_template(
        'agencias.html',
        agencias=[]
    )

@admin_bp.route('/empleados')
def empleados():
    return render_template(
        'empleados.html',
        empleados=[],
        cargos=[],
        agencias=[]
    )

@admin_bp.route('/asociados')
def asociados():
    return render_template(
        'asociados.html',
        asociados=[]
    )

@admin_bp.route('/reportes')
def reportes():
    return render_template(
        'reportes.html',
        asociados_reporte=[]
    )