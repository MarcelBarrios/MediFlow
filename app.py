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
from config import mongo 

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env
load_dotenv()

# Set Mongo URI
app.secret_key = os.getenv("SECRET_KEY")
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/mediflow")  # Load Mongo URI from .env
mongo = PyMongo(app)

app.mongo = mongo

# Now we can safely access the database collections
# These should be used after mongo is initialized
patient_collection = mongo.db.patients  # Now it should work

# Register blueprints
app.register_blueprint(base_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(patient_intake_bp, url_prefix='/intake')
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

# Run app
if __name__ == "__main__":
    app.run(debug=False, port=5001)


# Use this to debug.
# if __name__ == "__main__":
#     app.run(debug=True, port=5001)
