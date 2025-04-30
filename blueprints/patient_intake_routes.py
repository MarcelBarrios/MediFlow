from flask import Blueprint, render_template

patient_intake_bp = Blueprint('patient_intake', __name__, template_folder='../templates')

@patient_intake_bp.route("/patient_intake", methods=["GET"])
def patient_intake():
    return render_template("patient_intake.html")