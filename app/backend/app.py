from flask import Flask, redirect, url_for
from config import Config
from routes.auth import auth_bp
from db import test_tables
from routes.admin import admin_bp
from routes.asesor import asesor_bp
from routes.asociado import asociado_bp
from routes.reportes import reportes_bp

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)

app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['DEBUG'] = Config.DEBUG

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(asesor_bp)
app.register_blueprint(asociado_bp)
app.register_blueprint(reportes_bp)
@app.route('/')
def inicio():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)