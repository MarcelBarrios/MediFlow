from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import datetime

# Blueprint setup
patient_intake_bp = Blueprint('patient_intake', __name__)

# Route: Show patient intake form
@patient_intake_bp.route('/patient/<patient_id>', methods=['GET'])
def patient_intake_form(patient_id):
    patient_collection = current_app.mongo.db.patients
    patient = patient_collection.find_one({"mrn": patient_id})
    
    if not patient:
        flash("Patient not found.", "error")
        return redirect(url_for('appointments'))  

    return render_template('patient_intake.html', patient=patient)

@patient_intake_bp.route('/patient/<patient_id>/edit_photo', methods=["GET", "POST"])
def edit_photo(patient_id):
    patient_collection = current_app.mongo.db.patients
    patient = patient_collection.find_one({"mrn": patient_id})

    if not patient:
        flash("Patient not found.", "error")
        return redirect(url_for('home'))  # Adjust this based on your routing setup

    if request.method == "POST":
        # Get the new photo URL from the form
        new_photo_url = request.form.get("photo_url")

        if new_photo_url:
            # Update the patient's photo URL in the database
            patient_collection.update_one(
                {"mrn": patient_id},
                {"$set": {"photo_url": new_photo_url}}
            )
            flash("Photo updated successfully!", "success")
            return redirect(url_for('patient_intake.patient_intake_form', patient_id=patient_id))

        flash("Please provide a valid photo URL.", "error")

    # Render the form to edit the photo URL
    return render_template("edit_photo.html", patient=patient)


# Route: Save patient intake form
@patient_intake_bp.route("/save_intake", methods=["POST"])
def save_intake():
    try:
        data = request.form
        patient_id = data.get("patient_id")

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
            "notes": data.get("doctor_notes", "")
        }

        # Add health behavior info
        health_info = []

        # Alcohol
        if data.get('alcohol-use') == 'yes':
            health_info.append(f"Alcohol: Yes ({data.get('alcohol-frequency', 'N/A')} drinks/week)")
        else:
            health_info.append("Alcohol: No")

        # Smoking
        if data.get('smoking') == 'yes':
            health_info.append(f"Smoking: Yes ({data.get('smoking-frequency', 'N/A')} cigarettes/day)")
        else:
            health_info.append("Smoking: No")

        # Domestic violence
        dv_response = data.get('domestic-violence')
        if dv_response and dv_response != 'prefer not to answer':
            health_info.append(f"Domestic Violence: {dv_response.capitalize()}")

        # Add to notes section
        if health_info:
            new_record["notes"] += "\n\nPatient Health Info: " + ", ".join(health_info)

        # Insert the new record
        records_collection.insert_one(new_record)

        flash("Patient intake form saved successfully!", "success")
        return redirect(url_for('patient.patient_detail', patient_id=patient_id))

    except Exception as e:
        flash(f"Error saving intake form: {str(e)}", "error")
        return redirect(url_for('patient_intake.patient_intake_form', patient_id=patient_id))
