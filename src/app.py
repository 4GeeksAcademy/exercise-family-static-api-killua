"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
# from models import Person


app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# Create the jackson family object
jackson_family = FamilyStructure("Jackson")


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/members', methods=['GET'])
def handle_hello():
    # This is how you can use the Family datastructure by calling its methods
    try:
        members = jackson_family.get_all_members()
        return jsonify(members), 200  # ← esto devuelve una lista directamente
    except Exception:
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/members/<int:member_id>', methods=['GET'])
def get_single_member(member_id):
    try:
        member = jackson_family.get_member(member_id)
        if member is None:
            return jsonify({"error": "Member not found"}), 404
        return jsonify(member), 200
    except Exception:
        return jsonify({"error": "Internal Server Error"}), 500
    
@app.route('/members', methods=['POST'])
def create_member():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        # Validar campos obligatorios
        if "first_name" not in data or "age" not in data or "lucky_numbers" not in data:
            return jsonify({"error": "Missing required fields"}), 400

        # Construir nuevo miembro
        new_member = {
            "id": data.get("id"),  # puede venir o no
            "first_name": data["first_name"],
            "age": data["age"],
            "lucky_numbers": data["lucky_numbers"]
        }

        jackson_family.add_member(new_member)
        return jsonify(new_member), 200
    except Exception:
        return jsonify({"error": "Internal Server Error"}), 500
    
@app.route('/members/<int:member_id>', methods=['DELETE'])
def remove_member(member_id):
    try:
        was_deleted = jackson_family.delete_member(member_id)
        if not was_deleted:
            return jsonify({"error": "Member not found"}), 404
        return jsonify({"done": True}), 200
    except Exception:
        return jsonify({"error": "Internal Server Error"}), 500




# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
