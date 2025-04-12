from werkzeug.security import check_password_hash
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

# Collections
# tenants_collection = mongo.db.tenants


@app.route("/")
def base():
    return render_template("base.html")


@app.route("/appointments", methods=["GET"])
def appointments():
    return render_template("appointments.html")


@app.route("/patient_appointment", methods=["GET"])
def patient_appointment():
    return render_template("patient_appointment.html")


@app.route("/all_patients", methods=["GET"])
def all_patients():
    return render_template("all_patients.html")


# @app.route("/", methods=["GET"])
# def patient_procedures():
#     pass

@app.route("/patient", methods=["GET"])
def patient():
    return render_template("patient.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
