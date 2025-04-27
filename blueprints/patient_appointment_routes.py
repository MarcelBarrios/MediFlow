from flask import Blueprint, render_template

patient_appointment_bp = Blueprint('patient_appointment', __name__, template_folder='../templates')

@patient_appointment_bp.route("/patient_appointment", methods=["GET"])
def patient_appointment():
    return render_template("patient_appointment.html")