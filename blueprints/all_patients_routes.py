from flask import Blueprint, render_template, request, redirect, url_for
from .forms import CreateNewPatientForm

all_patients_bp = Blueprint('all_patients', __name__, template_folder='../templates')

@all_patients_bp.route("/all_patients", methods=["GET"])
def all_patients():
    return render_template("all_patients.html")

@all_patients_bp.route("/create_new_patient", methods=["GET", "POST"])
def create_patient():
    form = CreateNewPatientForm()

    if form.validate_on_submit():
        date_time = form.date_time.data
        mrn = form.random_mrn.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        dob = form.dob.data
        age = form.patient_age.data

        # save to database

        return redirect(url_for("all_patients.all_patients"))

    return render_template("create_new_patient.html", form=form)