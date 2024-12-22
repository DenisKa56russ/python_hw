from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps
import jwt
from datetime import datetime, timedelta
import os
from .accounts.routes import account_routes
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "dhsakjdhsajkdhaskdhasd"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Latte Gallery API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/swagger.json')
def swagger():
    return jsonify({
        "swagger": "2.0",
        "info": {
            "title": "Latte Gallery API",
            "version": "1.0"
        },
        "paths": {
            "/api/auth/register": {
                "post": {
                    "summary": "Register new user",
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "email": {"type": "string"},
                                    "password": {"type": "string"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "User created!"
                        },
                        "400": {
                            "description": "Bad request!"
                        },
                        "409": {
                            "description": "User already exists"
                        }
                    }
                }
            },
            "/api/auth/login": {
                "post": {
                    "summary": "Login user",
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successfull login"
                        },
                        "401": {
                            "description": "Bad username or password"
                        },
                         "400": {
                            "description":"Bad request"
                        }
                    }
                }
            },
            "/api/auth/protected": {
                "get": {
                    "summary": "Test protected route",
                    "security": [
                        {
                            "BearerAuth": []
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Success"
                        },
                        "403": {
                            "description": "Unauthorized"
                        }
                    }
                }
            }
        },
        "securityDefinitions": {
            "BearerAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization"
            }
        }
    })

SECRET_KEY = "dhsakjdhsajkdhaskdhasd"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.filter_by(id=data["id"]).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Bad request!'}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'message': 'User already exists'}), 409

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'message': 'Email already exists'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created!'}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Bad request!'}), 400

    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Bad username or password'}), 401

    token = jwt.encode({'id': user.id, 'exp': datetime.utcnow() + timedelta(minutes=30)}, SECRET_KEY,
                         algorithm="HS256")
    return jsonify({'token': token}), 200


@app.route('/api/auth/protected', methods=['GET'])
@token_required
def protected(current_user):
    return jsonify({"message": "Hello, " + current_user.username + "!"}), 200