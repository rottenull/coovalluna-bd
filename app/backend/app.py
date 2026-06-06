from flask import Flask, redirect, url_for
from config import Config
from routes.auth import auth_bp

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)

app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['DEBUG'] = Config.DEBUG

app.register_blueprint(auth_bp)

@app.route('/')
def inicio():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)