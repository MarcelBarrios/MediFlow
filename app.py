from blueprints.patient_routes import patient_bp
from blueprints.all_patients_routes import all_patients_bp
from blueprints.patient_intake_routes import patient_intake_bp
from blueprints.appointments_routes import appointments_bp
from blueprints.base_routes import base_bp
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime
import secrets
import certifi
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


# Set Mongo URI from environment
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI not found in environment variables!")

app.config["MONGO_URI"] = mongo_uri

# print("Loaded MONGO_URI:", os.getenv("MONGO_URI"))
# Initialize PyMongo / For deployment
# mongo = PyMongo(app, tlsCAFile=certifi.where())
# For testing locally, if not you'll get errors.
# mongo = PyMongo(app)

if "localhost" in mongo_uri or "127.0.0.1" in mongo_uri:
    mongo = PyMongo(app)
else:
    mongo = PyMongo(app, tlsCAFile=certifi.where())

app.mongo = mongo

# Access collections (must go after PyMongo setup)
new_patients_collection = mongo.db.patients

# Register blueprints

app.register_blueprint(base_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(patient_intake_bp)
app.register_blueprint(all_patients_bp)
app.register_blueprint(patient_bp)

# Test route - delete before deploying


@app.route("/test-db")
def test_db_connection():
    try:
        collections = mongo.db.list_collection_names()
        return jsonify({
            "status": "success",
            "message": "Connected to MongoDB!",
            "collections": collections
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/show-db")
def show_db():
    return f"Connected to MongoDB database: {mongo.db.name}"

# Run app
if __name__ == "__main__":
    app.run(debug=True, port=5001)