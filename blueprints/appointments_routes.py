from flask import Blueprint, render_template

appointments_bp = Blueprint('appointments', __name__, template_folder='../templates')

@appointments_bp.route("/appointments", methods=["GET"])
def appointments():
    return render_template("appointments.html")