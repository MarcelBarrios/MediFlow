from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_pymongo import PyMongo
# from pymongo import MongoClient
# from models.logic import logic_function
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId
import secrets  # To generate secure reset tokens
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Configure MongoDB with Flask-PyMongo
app.config["MONGO_URI"] = os.getenv(
    "MONGO_URI", "mongodb://localhost:27017/mediflow")
mongo = PyMongo(app)
app.mongo = mongo

# Collections
# mediflow_collection = mongo.db.mediflow
new_patients_collection = mongo.db.patients



# --- Import and Register Blueprints ---
from blueprints.base_routes import base_bp
from blueprints.appointments_routes import appointments_bp
from blueprints.patient_appointment_routes import patient_appointment_bp
from blueprints.all_patients_routes import all_patients_bp
from blueprints.patient_routes import patient_bp

# Register the blueprints with the Flask application instance
app.register_blueprint(base_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(patient_appointment_bp)
app.register_blueprint(all_patients_bp)
app.register_blueprint(patient_bp)


if __name__ == "__main__":
    app.run(debug=True, port=5002)
