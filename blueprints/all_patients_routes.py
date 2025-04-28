from flask import Blueprint, render_template

all_patients_bp = Blueprint('all_patients', __name__, template_folder='../templates')

@all_patients_bp.route("/all_patients", methods=["GET"])
def all_patients():
    return render_template("all_patients.html")

@all_patients_bp.route("/create_new_patient", methods=["GET", "POST"])
def create_patient():
    return render_template("create_new_patient.html")