from flask import Flask, jsonify, request
from pymongo import MongoClient
from flasgger import Swagger
import utilities
from bson.regex import Regex
from auth import auth_bp, token_required
from flask_bcrypt import Bcrypt
import os
from db import db

app = Flask(__name__)
Swagger= Swagger(app)
bcrypt = Bcrypt(app)
app.register_blueprint(auth_bp)

# Connect to MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI")

notes_collection = db["notes"]
notes_collection = db["notes"]#collection name

#local mongoDB
#client = MongoClient("mongodb://localhost:27017/")
#db = client.notes_db
#notes_collection = db.notes

@app.route('/notes', methods=['GET'])
@token_required
def get_notes(current_user_id):
    """
    Get All Notes
    ---
    tags:
      - Notes
    summary: Retrieve all notes for the logged-in user
    description: |
      Returns a list of all notes for the authenticated user.  
      You can filter results using the optional `search` query parameter.
    parameters:
      - name: search
        in: query
        required: false
        schema:
          type: string
        description: Keyword to search in title or text
    security:
      - bearerAuth: []
    responses:
      200:
        description: List of notes
        content:
          application/json:
            example:
              status: success
              data:
                - id: 64dfdsa76a89
                  title: Shopping List
                  text: Buy milk and eggs
                  freeze: false
                  created_at: 2025-08-10T12:00:00Z
    """
    search_query = request.args.get('search', None)
    query = {}
    if search_query:
        query = {
            "$or": [
                {"title": {"$regex": search_query, "$options": "i"}},
                {"text": {"$regex": search_query, "$options": "i"}}
            ]
        }
    
    notes = []
    for note in notes_collection.find({"user_id": current_user_id}):
        notes.append({
            'id': str(note['_id']),
            'title': note['title'],
            'text': note['text'],
            'freeze': note['freeze'],
            'created_at': note.get('created_at'),
            'updated_at': note.get('updated_at')
        })
    return jsonify({"status": "success", "data": notes}), 200


@app.route('/addNote', methods=['POST'])
@token_required
def add_note(current_user_id):
    """
    Add a new note
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
            - text
            - freeze
          properties:
            title:
              type: string
            text:
              type: string
            freeze:
              type: string
              enum: ["true", "false"]
    responses:
      200:
        description: Note added successfully
      400:
        description: Missing required fields
      403:
        description: Invalid field types
    """
    data = request.json
    if utilities.key_payload(data):
        return jsonify({"error": "Missing required fields"}), 400
    if utilities.freeze_payload(data):
        return jsonify({"error": "freeze value should be true or false"}), 400
    if utilities.key_type(data):
        return jsonify({"error": "title,text and freeze should be string"}), 403
    
    # Add timestamps
    data = utilities.add_timestamps(data)
    data["user_id"] = current_user_id 
    notes_collection.insert_one(data)
    return jsonify({"status": "success", "message": "Note added"}), 201

@app.route('/getNote', methods=['GET'])
@token_required
def get_note_by_name(current_user_id):
    """
    Get note by title
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
    responses:
      200:
        description: Note found
      400:
        description: Missing or invalid parameters
      403:
        description: Title should be string
    """
    data = request.json
    if "text" in data or "freeze" in data:
        return jsonify({"error": "Only 'title' is required to get note"}), 400
    if utilities.key_payload(data):
        return jsonify({"error": "Missing required field 'title'"}), 400
    if utilities.key_type(data):
        return jsonify({"error": "title should be string"}), 403

    note = notes_collection.find_one({"title": data['title'], "user_id": current_user_id})
    
    if not note:
        return jsonify({"status": "not found"}), 404

    return jsonify({
        "id": str(note['_id']),
        "title": note['title'],
        "text": note['text'],
        "freeze": note['freeze'],
        "created_at": note.get('created_at'),
        "updated_at": note.get('updated_at')
    }), 200


@app.route('/deleteNote', methods=['DELETE'])
@token_required
def delete_note_by_name(current_user_id):
    """
    Delete a note by title
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
    responses:
      200:
        description: Note deleted successfully
      400:
        description: Missing required field
      403:
        description: Title should be string
    """
    data = request.json
    if utilities.key_payload(data):
        return jsonify({"error": "Missing required field 'title'"}), 400
    if utilities.key_type(data):
        return jsonify({"error": "title should be string"}), 403

    result = notes_collection.delete_one({"title": data['title'], "user_id": current_user_id})
    if result.deleted_count > 0:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "not found"})


@app.route('/updateNote', methods=['PUT'])
@token_required
def update_note_by_name(current_user_id):
    """
    Update a note's text by title
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
            - text
          properties:
            title:
              type: string
            text:
              type: string
    responses:
      200:
        description: Note updated successfully
      400:
        description: Missing fields
      403:
        description: Invalid types or note frozen
    """
    data = request.json
    if utilities.key_payload(data):
        return jsonify({"error": "Missing 'title' in request body"}), 400
    if utilities.key_type(data):
        return jsonify({"error": "title should be string"}), 403
    if utilities.text_payload(data):
        return jsonify({"error": "Missing 'text' in request body"}), 400
    if utilities.text_type(data):
        return jsonify({"error": "text should be string"}), 403

    note = notes_collection.find_one({"title": data['title'], "user_id": current_user_id})
    if not note:
        return jsonify({"status": "not found"}), 404
    if note['freeze'] == "true":
        return jsonify({"error": "This note is frozen and cannot be edited"}), 403

    data = utilities.add_timestamps(data, is_update=True)
    notes_collection.update_one(
        {"title": data['title'], "user_id": current_user_id},
        {"$set": {"text": data['text']}}
    )
    return jsonify({"status": "success", "message": "Note updated"}), 200

@app.route('/insertSampleNotes', methods=['POST']) 
@token_required
def insert_sample_notes(current_user_id):
    """
    Insert multiple sample notes for the logged-in user
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - notes
          properties:
            notes:
              type: array
              items:
                type: object
                required:
                  - title
                  - text
                  - freeze
                properties:
                  title:
                    type: string
                  text:
                    type: string
                  freeze:
                    type: string
                    enum: ["true", "false"]
    responses:
      200:
        description: Sample notes inserted successfully
      400:
        description: Invalid data format
    """
    data = request.json
    notes = data.get("notes", [])

    if not isinstance(notes, list) or len(notes) == 0:
        return jsonify({"error": "Invalid or empty 'notes' array"}), 400

    for note in notes:
        if utilities.key_payload(note) or utilities.freeze_payload(note) or utilities.key_type(note):
            return jsonify({"error": "Invalid note format"}), 400
        note["user_id"] = current_user_id
        note = utilities.add_timestamps(note)  # 🔹 Add created_at & updated_at

    notes_collection.insert_many(notes)
    return jsonify({"status": "success", "message": f"{len(notes)} notes inserted"}), 200

@app.route('/freeze', methods=['PUT'])
@token_required 
def freeze_note(current_user_id):
    """
    Freeze or unfreeze a note
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
            - freeze
          properties:
            title:
              type: string
            freeze:
              type: string
              enum: ["true", "false"]
    responses:
      200:
        description: Note freeze status updated
      400:
        description: Missing or invalid data
      403:
        description: Invalid data types
    """
    data = request.json
    if utilities.key_payload(data):
        return jsonify({"error": "Missing 'title' in request body"}), 400
    if utilities.freeze_payload(data):
        return jsonify({"error": "freeze is missing"}), 400
    if utilities.key_type(data):
        return jsonify({"error": "title should be string"}), 403
    if utilities.freeze_type(data):
        return jsonify({"error": "'freeze' should be true or false"}), 400

    result = notes_collection.update_one(
        {"title": data['title'], "user_id": current_user_id},
        {"$set": {"freeze": data['freeze']}}
    )
    if result.modified_count > 0:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "not found"})


@app.route('/')
def home():
    """
    Welcome page
    ---
    responses:
      200:
        description: A welcome message
    """
    return "Welcome to Notes!"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5500)
