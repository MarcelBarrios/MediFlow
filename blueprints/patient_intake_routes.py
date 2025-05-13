from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from datetime import datetime, timezone
from bson import ObjectId

# Blueprint setup
patient_intake_bp = Blueprint('patient_intake', __name__)

# (new) changed route to have /intake to be different from patient_routes


@patient_intake_bp.route('/patient/<patient_id>/intake', methods=['GET'])
def patient_intake_form(patient_id):
    try:
        # (new) Get patient data from patients collection (ObjectId got convereted to string)
        patients_collection = current_app.mongo.db.patients
        patient = patients_collection.find_one({"_id": ObjectId(patient_id)})

        if patient:
            # Convert ObjectId to string
            patient['_id'] = str(patient['_id'])

            # (new) for appointment and chief complaint render:
            appointments_collection = current_app.mongo.db.appointments
            appointment = appointments_collection.find_one(
                {'patient_id': patient_id},
                # sort by date in descending order to get the most recent
                sort=[('date_time', -1)]
            )

            # (new) add appointment details to the patient object
            if appointment:
                patient['appointment_time'] = appointment.get(
                    'date_time', 'Not scheduled')
                patient['chief_complaint'] = appointment.get(
                    'chief_complaint', 'None recorded')

            else:
                patient['appointment_time'] = 'Not scheduled'
                patient['chief_complaint'] = 'None recorded'

            return render_template('patient_intake.html', patient=patient)
        else:
            flash("Patient not found.", "error")
            return redirect(url_for('all_patients.all_patients'))

    except Exception as e:
        flash(f"Error loading patient intake form: {str(e)}", "error")
        return redirect(url_for('all_patients.all_patients'))


@patient_intake_bp.route("/patient/<patient_id>/photo_edit", methods=["POST"])
def edit_photo(patient_id):
    patient_collection = current_app.mongo.db.patients
    patient = patient_collection.find_one({"_id": ObjectId(patient_id)})

    if not patient:
        return jsonify({"success": False, "message": "Patient not found"}), 400

    try:
        # Get the new photo URL from the request body
        data = request.get_json()
        new_photo_url = data.get("photo_url")

        if new_photo_url:
            # Update the patient's photo URL in the database
            patient_collection.update_one(
                {"_id": ObjectId(patient_id)},
                {"$set": {"photo_url": new_photo_url}}
            )
            return jsonify({"success": True, "message": "Photo updated successfully", "photo_url": new_photo_url})

        return jsonify({"success": False, "message": "Invalid photo URL"}), 400

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


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
            "date": datetime.now(timezone.utc),  # Store as offset-aware UTC
            "ordered_by": "Current User",  # Replace with actual user if available
            "details": f"Weight: {data.get('weight', 'N/A')} lbs, Height: {data.get('height', 'N/A')} inches, Temperature: {data.get('temperature', 'N/A')}°F",
            "notes": data.get("doctor_notes", "")
        }

        # Add health behavior info
        health_info = []

        # Alcohol
        if data.get('alcohol-use') == 'yes':
            health_info.append(
                f"Alcohol: Yes ({data.get('alcohol-frequency', 'N/A')} drinks/week)")
        else:
            health_info.append("Alcohol: No")

        # Smoking
        if data.get('smoking') == 'yes':
            health_info.append(
                f"Smoking: Yes ({data.get('smoking-frequency', 'N/A')} cigarettes/day)")
        else:
            health_info.append("Smoking: No")

        # Domestic violence
        dv_response = data.get('domestic-violence')
        if dv_response and dv_response != 'prefer not to answer':
            health_info.append(
                f"Domestic Violence: {dv_response.capitalize()}")

        # Add to notes section
        if health_info:
            new_record["notes"] += "\n\nPatient Health Info: " + \
                ", ".join(health_info)

        # Insert the new record
        records_collection.insert_one(new_record)

        flash("Patient intake form saved successfully!", "success")
        return redirect(url_for('patient.patient_detail', patient_id=patient_id))

    except Exception as e:
        flash(f"Error saving intake form: {str(e)}", "error")
        return redirect(url_for('patient_intake.patient_intake_form', patient_id=patient_id))
