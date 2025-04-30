from flask import Blueprint, render_template, current_app
from bson import ObjectId

patient_bp = Blueprint('patient', __name__, template_folder='../templates')

@patient_bp.route("/patient", methods=["GET"])
def patient():
    return render_template("patient.html")

@patient_bp.route("/patient/<patient_id>", methods=["GET"])
def patient_detail(patient_id):
  patient = current_app.mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
  if not patient:
    return "Patient not found.", 404
  return render_template("patient.html", patient=patient)