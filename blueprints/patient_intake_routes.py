from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import datetime
from bson import ObjectId

# Blueprint setup
patient_intake_bp = Blueprint('patient_intake', __name__)

# (new) changed route to have /intake to be different from patient_routes
@patient_intake_bp.route('/patient/<patient_id>/intake', methods=['GET'])
def patient_intake_form(patient_id):
    try:
        patients_collection = current_app.mongo.db.patients
        appointments_collection = current_app.mongo.db.appointments  # ✅

        patient = patients_collection.find_one({"_id": ObjectId(patient_id)})

        if patient:
            patient['_id'] = str(patient['_id'])

            # ✅ Get the most recent appointment for the patient
            latest_appointment = appointments_collection.find_one(
                {"patient_id": patient_id},
                sort=[("appointment_time", -1)]
            )

            return render_template(
                'patient_intake.html',
                patient=patient,
                appointment=latest_appointment  # ✅ pass it to the template
            )
        else:
            flash("Patient not found.", "error")
            return redirect(url_for('all_patients.all_patients'))

    except Exception as e:
        flash(f"Error loading patient intake form: {str(e)}", "error")
        return redirect(url_for('all_patients.all_patients'))

@patient_intake_bp.route('/patient/<patient_id>/edit_photo', methods=["GET", "POST"])
def edit_photo(patient_id):
    patient_intake_collection = current_app.mongo.db.patients
    patient_intake = patient_intake_collection.find_one({"_id": ObjectId(patient_id)})

    if not patient_intake:
        flash("Patient not found.", "error")
        return redirect(url_for('home'))  # Adjust this based on your routing setup

    if request.method == "POST":
        # Get the new photo URL from the form
        new_photo_url = request.form.get("photo_url")

        if new_photo_url:
            # Update the patient's photo URL in the database
            patient_intake_collection.update_one(
                {"_id": ObjectId(patient_id)},
                {"$set": {"photo_url": new_photo_url}}
            )
            flash("Photo updated successfully!", "success")
            return redirect(url_for('patient_intake.patient_intake_form', patient_id=patient_id))

        flash("Please provide a valid photo URL.", "error")

    # Render the form to edit the photo URL
    return render_template("edit_photo.html", patient_intake=patient_intake)


# Route: Save patient intake form
@patient_intake_bp.route("/save_intake", methods=["POST"])
def save_intake():
    try:
        data = request.form
        patient_id = data.get("patient_id")

        # ✅ Pull hidden patient info from the form
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        dob = data.get("dob")
        age = data.get("age")
        mrn = data.get("mrn")

        # Get the collection where patient records (like intake forms) are stored
        records_collection = current_app.mongo.db.records

        # Create new intake record
        new_record = {
            "patient_id": patient_id,
            "title": "Patient Intake Assessment",
            "category": "Appointment",
            "status": "Completed",
            "date": datetime.now(),
            "ordered_by": "Current User",  # Replace with actual user if available
            "details": f"Weight: {data.get('weight', 'N/A')} lbs, Height: {data.get('height', 'N/A')} inches, Temperature: {data.get('temperature', 'N/A')}°F",
            "notes": data.get("doctor_notes", ""),
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob,
            "age": age,
            "mrn": mrn
        }

        # Add health behavior info
        health_info = []

        if data.get('alcohol-use') == 'yes':
            health_info.append(f"Alcohol: Yes ({data.get('alcohol-frequency', 'N/A')} drinks/week)")
        else:
            health_info.append("Alcohol: No")

        if data.get('smoking') == 'yes':
            health_info.append(f"Smoking: Yes ({data.get('smoking-frequency', 'N/A')} cigarettes/day)")
        else:
            health_info.append("Smoking: No")

        dv_response = data.get('domestic-violence')
        if dv_response and dv_response != 'prefer not to answer':
            health_info.append(f"Domestic Violence: {dv_response.capitalize()}")

        if health_info:
            new_record["notes"] += "\n\nPatient Health Info: " + ", ".join(health_info)

        records_collection.insert_one(new_record)

        flash("Patient intake form saved successfully!", "success")
        return redirect(url_for('patient.patient_detail', patient_id=patient_id))

    except Exception as e:
        flash(f"Error saving intake form: {str(e)}", "error")
        return redirect(url_for('patient_intake.patient_intake_form', patient_id=patient_id))
