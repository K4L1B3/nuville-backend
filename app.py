from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_restx import Api, Resource
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './users-profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

load_dotenv('./.env')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/k4l1b3/projeto-stackover/instance/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'fallback_secret_key')  # Carregar da variável de ambiente
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB Max Size
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

api = Api(app, version='1.0', title='Projeto Integrador API', description='API para simular as funcionalidades do stack overflow')
ns = api.namespace('main', description='Operações principais')
db = SQLAlchemy(app)
jwt = JWTManager(app)




import os

@app.route('/dbpath')
def db_path():
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.split('sqlite:///')[-1]
        return os.path.abspath(db_path)
    else:
        return "O banco de dados não está usando SQLite."



# MAIN PARA EXECUTAR O APP EM PYTHON
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
