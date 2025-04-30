from flask import Blueprint, render_template, request, redirect, url_for, current_app
from .forms import CreateNewPatientForm
from bson import ObjectId

all_patients_bp = Blueprint("all_patients", __name__, template_folder="../templates")

@all_patients_bp.route("/all_patients", methods=["GET"])
def all_patients():
    patients_collection = current_app.mongo.db.patients
    patients = list(patients_collection.find())

    # Convert ObjectId to string for template rendering
    for patient in patients:
        patient["_id"] = str(patient["_id"])

    return render_template("all_patients.html", patients=patients)

@all_patients_bp.route("/create_new_patient", methods=["GET", "POST"])
def create_patient():
    form = CreateNewPatientForm()

    if form.validate_on_submit():
        new_patient = {
            "date_time": form.date_time.data.strftime('%Y-%m-%d %H:%M:%S'),
            "mrn": form.random_mrn.data,
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "dob": form.dob.data.strftime('%m/%d/%Y'),
            "age": form.patient_age.data
        }

        patients_collection = current_app.mongo.db.patients
        inserted = patients_collection.insert_one(new_patient)
        new_patient_id = str(inserted.inserted_id)

        return redirect(url_for("all_patients.all_patients"))

    return render_template("create_new_patient.html", form=form)