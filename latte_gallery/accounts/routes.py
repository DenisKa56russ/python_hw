from flask import Blueprint, request, jsonify
from latte_gallery import db, bcrypt, app
from latte_gallery.accounts.models import User
import jwt
from datetime import datetime, timedelta

accounts = Blueprint('accounts', __name__)

# Define a secret key for signing JWTs. Should be long and random
SECRET_KEY = app.config['SECRET_KEY']


def generate_jwt(user_id, username, roles):
    payload = {
        'user_id': user_id,
        'username': username,
        'roles': roles,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Токен действителен 1 час
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


@accounts.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Please provide username, email and password'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'User with this username already exists'}), 400

    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({'message': 'User with this email already exists'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201


@accounts.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Please provide username and password'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password'}), 401

    # Generate the JWT token
    token = generate_jwt(user.id, user.username, ['user'])

    return jsonify({'token': token}), 200


def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Missing authorization token'}), 401
        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()

            return f(current_user, *args, **kwargs)
        except:
            return jsonify({'message': 'Invalid token'}), 401

    return decorated


@accounts.route('/api/auth/protected', methods=['GET'])
@token_required
def protected(current_user):
    return jsonify({'message': f'Welcome, {current_user.username}! This is protected resource'}), 200