from flask import Blueprint, render_template, current_app, redirect, url_for, request
from bson import ObjectId
from flask import flash
from forms import CreateNewAppointmentForm
from config import mongo

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

@appointments_bp.route("/appointments/check_in/<appointment_id>", methods=["POST"])
def check_in_appointment(appointment_id):
    appointments_collection = current_app.mongo.db.appointments

    # Update the appointment to mark as checked in
    appointments_collection.update_one(
        {"_id": ObjectId(appointment_id)},
        {"$set": {"checked_in": True}}
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
                "date_time": form.date_time.data.strftime('%Y-%m-%d %H:%M:%S'),
                "mrn": patient["mrn"],
                "patient_name": f"{patient['first_name']} {patient['last_name']}",
                "age": patient["age"],
                "chief_complaint": form.chief_complaint.data,
                "checked_in": False
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
