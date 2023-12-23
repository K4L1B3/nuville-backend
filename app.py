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

# Modelos
#classe das questões
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='question', lazy=True)
    author = db.relationship('User', backref='questions', lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    author = db.relationship('User', backref='comments', lazy=True)  # Adicionado


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128))
    age = db.Column(db.Integer)
    profile_picture = db.Column(db.String(255)) # URL da imagem de perfil
    bookmarks = db.relationship('Bookmark', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class UserQuestionLike(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    like = db.Column(db.Boolean)  # True para like, False para dislike

class UserCommentLike(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), primary_key=True)
    like = db.Column(db.Boolean)  # True para like, False para dislike

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    
import os

@app.route('/dbpath')
def db_path():
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.split('sqlite:///')[-1]
        return os.path.abspath(db_path)
    else:
        return "O banco de dados não está usando SQLite."

# ROTAS:

# POST - Dar Like em Pergunta
@app.route('/questions/<int:question_id>/like', methods=['POST'])
@jwt_required()
def like_question(question_id):
    current_user_id = get_jwt_identity()
    existing_like = UserQuestionLike.query.filter_by(user_id=current_user_id, question_id=question_id).first()
    if existing_like:
        return jsonify({"message": "Already liked/disliked"}), 409
    new_like = UserQuestionLike(user_id=current_user_id, question_id=question_id, like=True)
    db.session.add(new_like)
    question = Question.query.get_or_404(question_id)
    question.likes += 1
    db.session.commit()
    return jsonify({"message": "Liked question successfully"})

# POST - Dar Dislike em Pergunta
@app.route('/questions/<int:question_id>/dislike', methods=['POST'])
@jwt_required()
def dislike_question(question_id):
    current_user_id = get_jwt_identity()
    existing_like = UserQuestionLike.query.filter_by(user_id=current_user_id, question_id=question_id).first()
    if existing_like:
        return jsonify({"message": "Already liked/disliked"}), 409
    new_like = UserQuestionLike(user_id=current_user_id, question_id=question_id, like=False)
    db.session.add(new_like)
    question = Question.query.get_or_404(question_id)
    question.dislikes += 1
    db.session.commit()
    return jsonify({"message": "Disliked question successfully"})

# GET - Listar Comentários de uma Pergunta
@app.route('/questions/<int:question_id>/comments', methods=['GET'])
def get_comments(question_id):
    comments = Comment.query.filter_by(question_id=question_id).order_by((Comment.likes - Comment.dislikes).desc()).all()
    comments_data = [
        {
            'content': c.content,
            'author_name': c.author.name,
            'author_profile_picture': c.author.profile_picture
        }
        for c in comments
    ]
    return jsonify(comments_data)

# POST - Adicionar Comentário
@app.route('/questions/<int:question_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(question_id):
    comment_data = request.json
    user_id = get_jwt_identity()
    new_comment = Comment(content=comment_data['content'], question_id=question_id, user_id=user_id)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({"message": "Comment added successfully"})

# PUT - Atualizar Comentário
@app.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    current_user_id = get_jwt_identity()
    comment = Comment.query.get(comment_id)
    if not comment or comment.user_id != current_user_id:
        return jsonify({"message": "Comment not found or unauthorized"}), 404
    data = request.json
    comment.content = data.get('content', comment.content)
    db.session.commit()
    return jsonify({"message": "Comment updated successfully"})

# DELETE - Deletar Comentário
@app.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    current_user_id = get_jwt_identity()
    comment = Comment.query.get(comment_id)

    if not comment:
        return jsonify({"message": "Comment not found"}), 404

    # Verifica se o usuário atual é o autor do comentário
    if comment.user_id != current_user_id:
        return jsonify({"message": "Unauthorized"}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "Comment deleted successfully"}), 200

# POST - Dar Like em Comentário
@app.route('/comments/<int:comment_id>/like', methods=['POST'])
@jwt_required()
def like_comment(comment_id):
    current_user_id = get_jwt_identity()
    existing_like = UserCommentLike.query.filter_by(user_id=current_user_id, comment_id=comment_id).first()
    if existing_like:
        return jsonify({"message": "Already liked/disliked this comment"}), 409
    new_like = UserCommentLike(user_id=current_user_id, comment_id=comment_id, like=True)
    db.session.add(new_like)
    comment = Comment.query.get_or_404(comment_id)
    comment.likes += 1
    db.session.commit()
    return jsonify({"message": "Liked comment successfully"})

# POST - Dar Dislike em Comentário
@app.route('/comments/<int:comment_id>/dislike', methods=['POST'])
@jwt_required()
def dislike_comment(comment_id):
    current_user_id = get_jwt_identity()
    existing_like = UserCommentLike.query.filter_by(user_id=current_user_id, comment_id=comment_id).first()
    if existing_like:
        return jsonify({"message": "Already liked/disliked this comment"}), 409
    new_like = UserCommentLike(user_id=current_user_id, comment_id=comment_id, like=False)
    db.session.add(new_like)
    comment = Comment.query.get_or_404(comment_id)
    comment.dislikes += 1
    db.session.commit()
    return jsonify({"message": "Disliked comment successfully"})

# POST - Registrar Usuário
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if data['password'] != data['confirm_password']:
        return jsonify({"message": "Passwords do not match"}), 400
    new_user = User(email=data['email'], name=data['name'], age=data['age'], profile_picture='default_profile_url')
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

# POST - Login do Usuário
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"message": "Invalid credentials"}), 401

# PUT - Atualizar Usuário
@app.route('/user/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    data = request.json
    user.name = data.get('name', user.name)
    user.age = data.get('age', user.age)
    if 'password' in data:
        user.set_password(data['password'])
    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200

# GET - Visualizar Bookmarks do Usuário
@app.route('/user/<int:user_id>/bookmarks', methods=['GET'])
@jwt_required()
def view_bookmarks(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"message": "Unauthorized access"}), 403
    bookmarks = Bookmark.query.filter_by(user_id=user_id).all()
    bookmarked_questions = [Question.query.get(bm.question_id) for bm in bookmarks]
    bookmarked_questions_data = [
        {
            'question_id': q.id,
            'title': q.title,
            'description': q.description
        }
        for q in bookmarked_questions if q is not None
    ]
    return jsonify(bookmarked_questions_data)

# POST - Adicionar Bookmark
@app.route('/user/<int:user_id>/bookmark/<int:question_id>', methods=['POST'])
@jwt_required()
def add_bookmark(user_id, question_id):
    new_bookmark = Bookmark(user_id=user_id, question_id=question_id)
    db.session.add(new_bookmark)
    db.session.commit()
    return jsonify({"message": "Bookmark added successfully"}), 201

# DELETE - Remover Bookmark
@app.route('/user/<int:user_id>/bookmark/<int:question_id>', methods=['DELETE'])
@jwt_required()
def remove_bookmark(user_id, question_id):
    bookmark = Bookmark.query.filter_by(user_id=user_id, question_id=question_id).first()
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        return jsonify({"message": "Bookmark removed successfully"}), 200
    return jsonify({"message": "Bookmark not found"}), 404

# GET - Visualizar Histórico de Perguntas do Usuário
@app.route('/user/<int:user_id>/history', methods=['GET'])
@jwt_required()
def view_history(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    questions = Question.query.filter_by(user_id=user_id).all()
    return jsonify([{'title': q.title, 'description': q.description} for q in questions])

# Função allowed_file e rota de upload de imagem de perfil
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload/<int:user_id>', methods=['POST'])
@jwt_required()
def upload_file(user_id):
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        relative_path = os.path.join('users-profiles', filename)  # Salva caminho relativo

        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        user.profile_picture = relative_path
        db.session.commit()
        return jsonify({"message": "File uploaded successfully"}), 200
        
# MAIN PARA EXECUTAR O APP EM PYTHON
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
   