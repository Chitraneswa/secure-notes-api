import os
import certifi
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from config import MONGO_URI
import jwt
import datetime
from config import SECRET_KEY
from functools import wraps
from db import db

'''Blueprint: allows you to organize routes in separate files.

request: lets you access the POST data (username, password).

jsonify: formats JSON responses.

MongoClient: used to connect to MongoDB.

Bcrypt: hashes passwords securely.

MONGO_URI: your MongoDB connection string, loaded from config.py.'''

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# Use same connection method as app.py
MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")

notes_collection = db["notes"]
users = db["users"] 

'''Blueprint: lets you group routes separately (auth routes).

request: to get request data.

bcrypt: used for hashing passwords.

jwt: used to encode/decode tokens.

client: connects to MongoDB database.'''

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    User Signup
    ---
    tags:
      - Authentication
    summary: Register a new user
    description: Create a new user account with username and password.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
                example: johndoe
              password:
                type: string
                example: mySecurePass123
    responses:
      201:
        description: User registered successfully
        content:
          application/json:
            example:
              message: User created successfully
              token: your_jwt_token_here
      400:
        description: User already exists or invalid input
    """
    data = request.json or {}

    # 🔹 Validate request
    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password required"}), 400

    # 🔹 Check if user already exists
    if users.find_one({"username": data["username"]}):
        return jsonify({"error": "User already exists"}), 400

    # 🔹 Hash password
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    # 🔹 Save new user
    inserted_user = users.insert_one({
        'username': data['username'],
        'password': hashed_pw
    })

    # 🔹 Auto-generate token on signup
    token = jwt.encode({
        'user_id': str(inserted_user.inserted_id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        'status': 'User registered successfully',
        'token': token  # 🔹 return token so user can start calling protected APIs immediately
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    #Create JWT Token
    '''jwt.encode(payload, key, algorithm):
    Payload contains:
    username: who the user is
    exp: when the token expires (1 hour)
    SECRET_KEY: from config.py
    HS256: encryption algorithm used'''
    data = request.json or {}

    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password required"}), 400

    user = users.find_one({"username": data["username"]})
    if not user or not bcrypt.check_password_hash(user["password"], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    # 🔹 Create JWT token
    token = jwt.encode({
        'user_id': str(user['_id']),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "status": "success",
        "token": token
    }), 200

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401

        return f(current_user_id, *args, **kwargs)  # 🔹 Pass user ID to route
    return decorated




