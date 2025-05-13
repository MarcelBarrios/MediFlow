# blueprints/patient_routes.py
from flask import Blueprint, render_template, current_app, request, abort, redirect, url_for, flash, jsonify
from bson import ObjectId
from datetime import datetime, timezone
# Removed: from config import mongo # Using current_app.mongo.db instead

patient_bp = Blueprint('patient', __name__, template_folder='../templates')

# --- Helper Data (STATUS_STYLES, CATEGORY_STYLES, FILTER_MAP) ---
STATUS_STYLES = {
    "Completed": "bg-green-100 text-green-800",
    "Pending": "bg-orange-100 text-orange-800",
    "Cancelled": "bg-red-100 text-red-800",
    "Scheduled": "bg-blue-100 text-blue-700",  # Added from previous step
    # Add other statuses as needed
}
DEFAULT_STATUS_STYLE = "bg-gray-100 text-gray-800"

CATEGORY_STYLES = {
    "Lab Test": "bg-red-100 text-red-800",
    "Imaging": "bg-yellow-100 text-yellow-800",
    "Surgery": "bg-purple-100 text-purple-800",
    "Medication": "bg-teal-100 text-teal-800",
    "Appointment": "bg-blue-100 text-blue-800",
    "Specialist Consult": "bg-indigo-100 text-indigo-800",  # Added from previous step
    "Cardiac": "bg-pink-100 text-pink-800",           # Added from previous step
    "Visit Note": "bg-lime-100 text-lime-800",        # Added from previous step
    # Add other categories as needed
}
DEFAULT_CATEGORY_STYLE = "bg-gray-100 text-gray-800"

FILTER_MAP = {
    "lab-test": {"field": "category", "value": "Lab Test"},
    "imaging": {"field": "category", "value": "Imaging"},
    "surgery": {"field": "category", "value": "Surgery"},
    "medications": {"field": "category", "value": "Medication"},
    # Maps to 'Appointment' category
    "past-appointments": {"field": "category", "value": "Appointment"},
    "specialist-consult": {"field": "category", "value": "Specialist Consult"},
    "cardiac": {"field": "category", "value": "Cardiac"},
    "visit-note": {"field": "category", "value": "Visit Note"},
    "completed": {"field": "status", "value": "Completed"},
    "pending": {"field": "status", "value": "Pending"},
    "cancelled": {"field": "status", "value": "Cancelled"},
    "scheduled": {"field": "status", "value": "Scheduled"},
}


def format_date_for_display(date_val):
    """Formats a datetime object or various date string formats for display."""
    if isinstance(date_val, datetime):
        # If it's aware, you might want to convert to local time here for display
        # For now, just format it
        # Example: May 12, 2025 09:30 PM UTC
        return date_val.strftime('%B %d, %Y %I:%M %p %Z')
    if isinstance(date_val, str):
        try:
            dt_obj = get_sortable_date_object(
                date_val)  # Use the robust parser
            if dt_obj and dt_obj != datetime.min:  # Check if parsing was successful
                return dt_obj.strftime('%B %d, %Y %I:%M %p %Z')
            return date_val  # Return original string if parsing failed
        except ValueError:
            return date_val
    return str(date_val) if date_val is not None else "N/A"


def get_sortable_date_object(date_val):
    """
    Attempts to convert a date value (datetime, ISO string, YYYY-MM-DD string)
    into an offset-aware UTC datetime object for sorting. Returns datetime.min (naive) on failure.
    """
    if isinstance(date_val, datetime):
        if date_val.tzinfo is None or date_val.tzinfo.utcoffset(date_val) is None:
            # If naive, assume UTC (or local and convert to UTC if appropriate for your app logic)
            return date_val.replace(tzinfo=timezone.utc)
        return date_val  # It's already aware

    if isinstance(date_val, str):
        try:  # Try ISO format (often includes 'Z' or offset)
            dt = datetime.fromisoformat(date_val.replace("Z", "+00:00"))
            if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
                # Make it UTC aware if parsed as naive
                return dt.replace(tzinfo=timezone.utc)
            return dt  # It was parsed as aware
        except ValueError:
            try:  # Try YYYY-MM-DD format (will be naive)
                dt = datetime.strptime(date_val, '%Y-%m-%d')
                return dt.replace(tzinfo=timezone.utc)  # Assume UTC
            except ValueError:
                # Fallback: aware min datetime
                return datetime.min.replace(tzinfo=timezone.utc)
    # Fallback for None or other types, make it aware min datetime
    return datetime.min.replace(tzinfo=timezone.utc)


@patient_bp.route("/patient", methods=["GET"])
def patient_generic():
    flash("Please select a patient first.", "info")
    return redirect(url_for('all_patients.all_patients'))

# edit photo route


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
        patient_collection = current_app.mongo.db.patients
        obj_id = ObjectId(patient_id)
        patient = patient_collection.find_one({"_id": obj_id})

        if not patient:
            flash('Patient not found', 'error')
            return redirect(url_for('patient.patient_generic'))

    except Exception as e:
        flash(f'Error loading patient details: {str(e)}', 'error')
        return redirect(url_for('patient.patient_generic'))

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
    patient_id_str_for_query = str(obj_id)
    all_records = list(records_collection.find(
        {"patient_id": patient_id_str_for_query}))

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
        record_copy = record.copy()
        status = record_copy.get("status", "Unknown")
        category = record_copy.get("category", "Unknown")

        record_copy["status_style"] = STATUS_STYLES.get(
            status, DEFAULT_STATUS_STYLE)
        record_copy["category_style"] = CATEGORY_STYLES.get(
            category, DEFAULT_CATEGORY_STYLE)

        # Get the date value, which might be datetime or string
        date_val = record_copy.get("date")
        # Convert to aware datetime object for consistent handling
        aware_dt_obj = get_sortable_date_object(date_val)

        # For display in template (string)
        record_copy["formatted_date_for_display"] = format_date_for_display(
            aware_dt_obj)

        # For pre-filling edit form (YYYY-MM-DDTHH:MM)
        if aware_dt_obj and aware_dt_obj != datetime.min.replace(tzinfo=timezone.utc):
            record_copy["form_edit_date"] = aware_dt_obj.strftime(
                '%Y-%m-%dT%H:%M')
        else:
            # Or original string if preferred and not a date
            record_copy["form_edit_date"] = ""

        records_for_template.append(record_copy)

    # Sort using the helper function that ensures all keys are aware datetime objects
    records_for_template.sort(
        key=lambda r: get_sortable_date_object(r.get("date")), reverse=True)

    return render_template(
        "patient.html",
        patient=patient,
        records=records_for_template,
        active_filters=filter_args
    )

# --- NEW ROUTE: Update Patient Photo URL ---


@patient_bp.route("/patient/<patient_id>/update_photo_url", methods=["POST"])
def update_patient_photo(patient_id):
    try:
        obj_id = ObjectId(patient_id)
        data = request.get_json()
        new_photo_url = data.get("photo_url")

        # Basic validation
        if not new_photo_url or not isinstance(new_photo_url, str):
            return jsonify({"success": False, "message": "Invalid photo URL provided."}), 400

        patients_collection = current_app.mongo.db.patients
        result = patients_collection.update_one(
            {"_id": obj_id},
            {"$set": {"photo_url": new_photo_url}}
        )

        if result.matched_count == 0:
            return jsonify({"success": False, "message": "Patient not found."}), 404

        flash("Patient photo updated successfully!", "success")
        return jsonify({"success": True, "message": "Photo updated successfully.", "new_photo_url": new_photo_url})

    except Exception as e:
        current_app.logger.error(f"Error updating patient photo: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

# --- NEW ROUTE: Update Appointment Record ---


@patient_bp.route("/record/<record_id>/update_appointment", methods=["POST"])
def update_appointment_record(record_id):
    try:
        record_obj_id = ObjectId(record_id)
        data = request.get_json()

        # Fields that can be updated for an appointment
        # Ensure your frontend sends these fields in the JSON payload
        allowed_fields = ["title", "details",
                          "notes", "date", "status", "ordered_by"]
        update_data = {}

        for field in allowed_fields:
            if field in data:
                if field == "date":  # Special handling for date
                    # Convert incoming date string (expected from datetime-local input) to datetime object for DB
                    dt_obj = get_datetime_object(data[field])
                    if dt_obj:
                        update_data[field] = dt_obj
                    else:
                        # Handle invalid date string if necessary, or skip update for date
                        # For now, we'll skip if it's invalid to avoid storing bad data
                        current_app.logger.warning(
                            f"Invalid date format received for record {record_id}: {data[field]}")
                else:
                    update_data[field] = data[field]

        if not update_data:
            return jsonify({"success": False, "message": "No update data provided."}), 400

        records_collection = current_app.mongo.db.records
        # Ensure we only update records that are appointments and belong to the record_id
        result = records_collection.update_one(
            # Make sure to only update if it's an appointment
            {"_id": record_obj_id, "category": "Appointment"},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            return jsonify({"success": False, "message": "Appointment record not found or not an appointment."}), 404

        if result.modified_count == 0 and result.matched_count == 1:
            return jsonify({"success": True, "message": "No changes detected in appointment record."})

        flash("Appointment record updated successfully!", "success")
        return jsonify({"success": True, "message": "Appointment record updated successfully."})

    except Exception as e:
        current_app.logger.error(f"Error updating appointment record: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500
