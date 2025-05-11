from flask import Blueprint, render_template, current_app, request, abort, redirect, url_for, flash, jsonify
from bson import ObjectId
from datetime import datetime
from config import mongo

patient_bp = Blueprint('patient', __name__, template_folder='../templates')

STATUS_STYLES = {
    "Completed": "bg-green-100 text-green-800",
    "Pending": "bg-orange-100 text-orange-800",
    "Cancelled": "bg-red-100 text-red-800",
}
DEFAULT_STATUS_STYLE = "bg-gray-100 text-gray-800"

CATEGORY_STYLES = {
    "Lab Test": "bg-red-100 text-red-800",
    "Imaging": "bg-yellow-100 text-yellow-800",
    "Surgery": "bg-purple-100 text-purple-800",
    "Medication": "bg-teal-100 text-teal-800",
    "Appointment": "bg-blue-100 text-blue-800",
}
DEFAULT_CATEGORY_STYLE = "bg-gray-100 text-gray-800"

FILTER_MAP = {
    "lab-test": {"field": "category", "value": "Lab Test"},
    "imaging": {"field": "category", "value": "Imaging"},
    "surgery": {"field": "category", "value": "Surgery"},
    "medications": {"field": "category", "value": "Medication"},
    "past-appointments": {"field": "category", "value": "Appointment"},
    "completed": {"field": "status", "value": "Completed"},
    "pending": {"field": "status", "value": "Pending"},
    "cancelled": {"field": "status", "value": "Cancelled"},
}

def format_date(date_obj):
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%B %d, %Y')
    if isinstance(date_obj, str):
        try:
            return datetime.strptime(date_obj, '%Y-%m-%d').strftime('%B %d, %Y')
        except ValueError:
            pass
    return date_obj

@patient_bp.route("/patient", methods=["GET"])
def patient_generic():
    flash("Please select a patient first.", "info")
    return redirect(url_for('all_patients.all_patients'))

# added Edit Photo option
@patient_bp.route("/patient/<patient_id>/edit_photo", methods=["POST"])
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

# edited Patient Details in order for Save Intake to save to database and Records.
@patient_bp.route("/patient/<patient_id>/record", methods=["GET"])
def patient_detail(patient_id):
    try:
        # Define patient_collection using current_app
        patient_collection = current_app.mongo.db.patients
        obj_id = ObjectId(patient_id)

        # Find the patient
        patient = patient_collection.find_one({"_id": obj_id})

        # Check if patient was found
        if not patient:
            flash('Patient not found', 'error')
            return redirect(url_for('patient.patient_generic'))  # Redirect to a generic page or list

    except Exception as e:
        flash(f'Error loading patient details: {str(e)}', 'error')
        return redirect(url_for('patient.patient_generic'))  # Redirect to a generic page or list


    active_category_filters = []
    active_status_filters = []
    filter_args = request.args.getlist('filter')

    for filt in filter_args:
        if filt in FILTER_MAP:
            map_info = FILTER_MAP[filt]
            if map_info["field"] == "category":
                active_category_filters.append(map_info["value"])
            elif map_info["field"] == "status":
                active_status_filters.append(map_info["value"])

    records_collection = current_app.mongo.db.records
    all_records = list(records_collection.find({"patient_id": str(patient_id)}))
    filtered_records = []

    filters_selected = bool(active_category_filters or active_status_filters)

    for record in all_records:
        if not filters_selected:
            filtered_records.append(record)
        else:
            category_match = (not active_category_filters or
                              record.get("category") in active_category_filters)
            status_match = (not active_status_filters or
                            record.get("status") in active_status_filters)
            if category_match and status_match:
                filtered_records.append(record)

    records_for_template = []
    for record in filtered_records:
        status = record.get("status", "Unknown")
        category = record.get("category", "Unknown")
        record_copy = record.copy()
        record_copy["status_style"] = STATUS_STYLES.get(status, DEFAULT_STATUS_STYLE)
        record_copy["category_style"] = CATEGORY_STYLES.get(category, DEFAULT_CATEGORY_STYLE)
        record_copy["formatted_date"] = format_date(record.get("date"))
        records_for_template.append(record_copy)

    records_for_template.sort(key=lambda r: r.get("date", ""), reverse=True)

    return render_template(
        "patient.html",
        patient=patient,  
        records=records_for_template,
        active_filters=filter_args
    )