from flask import Blueprint, render_template, current_app, redirect, url_for, request
from bson import ObjectId
from flask import flash
from forms import CreateNewAppointmentForm
from config import mongo
from datetime import datetime

appointments_bp = Blueprint('appointments', __name__, template_folder='../templates')

@appointments_bp.route("/appointments", methods=["GET"])
def appointments():
    appointments_collection = current_app.mongo.db.appointments
    appointments_data = list(appointments_collection.find())

    # (new) Debug: Print first appointment structure (new add for patient_intake debug)
    if appointments_data:
        print("First appointment:", appointments_data[0])
    
    # (new) Convert ObjectId to string for template rendering
    for appointment in appointments_data:
        appointment["_id"] = str(appointment["_id"])

    return render_template("appointments.html", appointments=appointments_data)

# This route updates an appointment's status in the database when the dropdown is changed
@appointments_bp.route("/appointments/update_status/<appointment_id>", methods=["POST"])
def update_status(appointment_id):
    new_status = request.form.get("status")
    appointments_collection = current_app.mongo.db.appointments
    appointments_collection.update_one(
        {"_id": ObjectId(appointment_id)},
        {"$set": {"status": new_status}}
    )
    return redirect(url_for("appointments.appointments"))

@appointments_bp.route("/new_appointment", methods=["GET", "POST"])
def new_appointment():
    form = CreateNewAppointmentForm()
    patients_collection = current_app.mongo.db.patients

    if form.validate_on_submit():
        # Try to find matching patient
        patient = patients_collection.find_one({
            "first_name": form.patient_first_name.data,
            "last_name": form.patient_last_name.data
        })

        if patient:
            new_appointment = {
                # (new) added patient_id
                "patient_id": str(patient["_id"]),
                "date_time": form.date_time.data.strftime('%m/%d/%Y %I:%M %p'),
                "mrn": patient["mrn"],
                "patient_name": f"{patient['first_name']} {patient['last_name']}",
                "age": patient["age"],
                "chief_complaint": form.chief_complaint.data,
                "status": "Due for appointment"
            }

            appointments_collection = current_app.mongo.db.appointments
            appointments_collection.insert_one(new_appointment)

            return redirect(url_for("appointments.appointments"))

        else:
            flash("No matching patient found.")
            all_patients = list(patients_collection.find({}, {"first_name": 1, "last_name": 1, "mrn": 1,  "age": 1}))
            for p in all_patients:
                p["_id"] = str(p["_id"])
            return render_template("new_appointment.html", form=form, no_match=True, patients=all_patients)

    # Always pass patients to the template (for autocomplete)
    all_patients = list(patients_collection.find({}, {"first_name": 1, "last_name": 1, "mrn": 1,  "age": 1}))
    for p in all_patients:
        p["_id"] = str(p["_id"])

    return render_template("new_appointment.html", form=form, patients=all_patients)

@appointments_bp.route("/appointments/update", methods=["POST"])
def update_appointment():
    appointments_collection = current_app.mongo.db.appointments
    appointment_id = request.form["appointment_id"]
    unformatted_date = request.form["date_time"]
    new_complaint = request.form["chief_complaint"]

    # Format date to match the original format
    formatted_date = datetime.strptime(unformatted_date, "%Y-%m-%dT%H:%M").strftime('%m/%d/%Y %I:%M %p')

    appointments_collection.update_one(
        {"_id": ObjectId(appointment_id)},
        {"$set": {
            "date_time": formatted_date,
            "chief_complaint": new_complaint
        }}
    )

    return redirect(url_for("appointments.appointments"))
