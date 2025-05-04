from flask import Blueprint, render_template, current_app, redirect, url_for
from bson import ObjectId

appointments_bp = Blueprint('appointments', __name__, template_folder='../templates')

@appointments_bp.route("/appointments", methods=["GET"])
def appointments():
    appointments_collection = current_app.mongo.db.appointments
    appointments_data = list(appointments_collection.find())

    # Convert ObjectId to string for template rendering
    for appointment in appointments_data:
        appointment["_id"] = str(appointment["_id"])

    print("Appointments Data:", appointments_data)  # Add this line
    return render_template("appointments.html", appointments=appointments_data)


@appointments_bp.route("/new_appointment", methods=["GET"])
def new_appointment():
    return render_template("new_appointment.html")