from flask import Flask, jsonify
from flask import request, jsonify
from functools import wraps
import jwt
from config import SECRET_KEY

#Validation Utilities
def key_payload(data):
    if "title" not in data:
        return True
    
def text_payload(data):
    if "text" not in data:
        return True
    
def freeze_type(data):
    if data['freeze']!= "true" and data['freeze']!="false" :
        return True
    
def key_type(data):    
    if type(data['title']) is not str:
        return True
def text_type(data):    
    if type(data['text']) is not str :
        return True
       
def is_frozen(data):
    if data['freeze'] == "true":
        return True
    
def freeze_payload(data):
    if "freeze" not in data:
        return True
    
#JWT Authentication Decorator
def token_required(f):
    #@wraps(f) preserves the original function’s metadata (like its name).
    @wraps(f)
    #decorated is the new wrapped function that will run instead of f, adding auth checks first.
    def decorated(*args, **kwargs):
        token = None

        # Expect header: Authorization: Bearer <token>
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify({"msg": "Token missing"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.username = payload["username"]  # Attach username to request
        except jwt.ExpiredSignatureError:
            return jsonify({"msg": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"msg": "Invalid token"}), 401

        return f(*args, **kwargs) #If all checks pass, run the original function (e.g. `get_notes`).
    return decorated

'''when user calls GET /notes
    Authorization: Bearer eyJhbGciOi...
    @token_required does:
    Check the Authorization header.
    Extract the token.
    Decode and validate it.
    Attach username to the request.
    Run your get_notes() function with the verified user.'''

def find_note_by_title(collection, title):
    """Find a single note by its title."""
    return collection.find_one({"title": title})

def add_timestamps(data, is_update=False):
    """Add created_at or updated_at timestamps to the note data."""
    from datetime import datetime
    if not is_update:
        data["created_at"] = datetime.utcnow().isoformat()
    data["updated_at"] = datetime.utcnow().isoformat()
    return data
