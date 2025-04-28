from flask import Blueprint, render_template

appointments_bp = Blueprint('appointments', __name__, template_folder='../templates')

@appointments_bp.route("/appointments", methods=["GET"])
def appointments():
    return render_template("appointments.html")


@appointments_bp.route("/new_appointment", methods=["GET"])
def new_appointment():
    return render_template("new_appointment.html")


