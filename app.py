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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'fallback_secret_key')  # Carregar da variável de ambiente
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB Max Size
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

api = Api(app, version='1.0', title='Projeto Integrador API', description='API para simular as funcionalidades do stack overflow')
ns = api.namespace('main', description='Operações principais')
db = SQLAlchemy(app)
jwt = JWTManager(app)


# GET - Listar Todas as Perguntas
@app.route('/questions', methods=['GET'])
def get_questions():
    questions = Question.query.order_by((Question.likes - Question.dislikes).desc()).all()
    questions_data = [
        {
            'title': q.title,
            'description': q.description,
            'author_name': q.author.name,
            'author_profile_picture': q.author.profile_picture
        }
        for q in questions
    ]
    return jsonify(questions_data)

# GET - Buscar Perguntas por Título
@app.route('/questions/search', methods=['GET'])
def search_questions():
    title_query = request.args.get('title', '')
    questions = Question.query.filter(Question.title.like(f'%{title_query}%')).order_by((Question.likes - Question.dislikes).desc()).all()
    questions_data = [
        {
            'id': q.id,
            'title': q.title,
            'description': q.description,
            'author_name': q.author.name,
            'author_profile_picture': q.author.profile_picture
        }
        for q in questions
    ]
    return jsonify(questions_data)

# POST - Adicionar Pergunta
@app.route('/questions', methods=['POST'])
@jwt_required()
def add_question():
    question_data = request.json
    user_id = get_jwt_identity()
    new_question = Question(title=question_data['title'], description=question_data['description'], user_id=user_id)
    db.session.add(new_question)
    db.session.commit()
    return jsonify({"message": "Question added successfully"})

# PUT - Atualizar Pergunta
@app.route('/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
def update_question(question_id):
    current_user_id = get_jwt_identity()
    question = Question.query.get(question_id)
    if not question or question.user_id != current_user_id:
        return jsonify({"message": "Question not found or unauthorized"}), 404
    data = request.json
    question.title = data.get('title', question.title)
    question.description = data.get('description', question.description)
    db.session.commit()
    return jsonify({"message": "Question updated successfully"})

# DELETE - Deletar Pergunta
@app.route('/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    current_user_id = get_jwt_identity()
    question = Question.query.get(question_id)

    if not question:
        return jsonify({"message": "Question not found"}), 404

    # Verifica se o usuário atual é o autor da pergunta
    if question.user_id != current_user_id:
        return jsonify({"message": "Unauthorized"}), 403

    db.session.delete(question)
    db.session.commit()
    return jsonify({"message": "Question deleted successfully"}), 200


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
