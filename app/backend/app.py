import os
from flask import Flask, redirect, url_for
from config import config
from routes.auth import auth_bp

base_dir = os.path.dirname(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'frontend', 'templates')
static_dir = os.path.join(base_dir, 'frontend', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['secret_key'] = config.secret_key

app.register_blueprint(auth_bp)

@app.route('/')
def inicio():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=config.debug)