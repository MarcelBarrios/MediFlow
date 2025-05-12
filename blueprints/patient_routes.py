# blueprints/patient_routes.py
from flask import Blueprint, render_template, current_app, request, abort, redirect, url_for, flash, jsonify
from bson import ObjectId
from datetime import datetime
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


def format_date_for_display(date_obj):
    """Formats a datetime object or a date string for display."""
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%B %d, %Y')
    if isinstance(date_obj, str):
        try:
            # Attempt to parse common ISO-like format first
            dt = datetime.fromisoformat(date_obj.replace("Z", "+00:00"))
            return dt.strftime('%B %d, %Y')
        except ValueError:
            try:
                # Attempt to parse YYYY-MM-DD
                dt = datetime.strptime(date_obj, '%Y-%m-%d')
                return dt.strftime('%B %d, %Y')
            except ValueError:
                return date_obj  # Return original string if parsing fails
    return str(date_obj) if date_obj is not None else "N/A"


def get_datetime_object(date_val):
    """Converts a date string (YYYY-MM-DD or ISO) or datetime object to a datetime object for DB storage/comparison."""
    if isinstance(date_val, datetime):
        return date_val
    if isinstance(date_val, str):
        try:  # Try ISO format first (common from datetime-local input)
            return datetime.fromisoformat(date_val.replace("Z", "+00:00"))
        except ValueError:
            try:  # Try YYYY-MM-DD
                return datetime.strptime(date_val, '%Y-%m-%d')
            except ValueError:
                return None  # Or raise an error, or return a default
    return None


@patient_bp.route("/patient", methods=["GET"])
def patient_generic():
    flash("Please select a patient first.", "info")
    return redirect(url_for('all_patients.all_patients'))


@patient_bp.route("/patient/<patient_id_from_url>/record", methods=["GET"])
def patient_detail(patient_id_from_url):
    try:
        patient_collection = current_app.mongo.db.patients
        obj_id = ObjectId(patient_id_from_url)
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

        # For display in template (string)
        record_copy["formatted_date_for_display"] = format_date_for_display(
            record_copy.get("date"))

        # For pre-filling edit form (YYYY-MM-DDTHH:MM if datetime, or YYYY-MM-DD if string)
        date_val = record_copy.get("date")
        if isinstance(date_val, datetime):
            record_copy["form_edit_date"] = date_val.strftime('%Y-%m-%dT%H:%M')
        elif isinstance(date_val, str):
            try:  # if date is YYYY-MM-DD string
                dt_obj = datetime.strptime(date_val, '%Y-%m-%d')
                record_copy["form_edit_date"] = dt_obj.strftime(
                    '%Y-%m-%dT%H:%M')  # Convert to datetime-local format
            except ValueError:
                # Keep as is if not parsable to YYYY-MM-DD
                record_copy["form_edit_date"] = date_val
        else:
            record_copy["form_edit_date"] = ""

        records_for_template.append(record_copy)

    # Sorting: Convert dates to datetime objects for reliable sorting
    min_datetime_for_sorting = datetime.min

    def get_sortable_date(r):
        date_val = r.get("date")
        if isinstance(date_val, datetime):
            return date_val
        if isinstance(date_val, str):
            try:
                return datetime.fromisoformat(date_val.replace("Z", "+00:00"))
            except ValueError:
                try:
                    return datetime.strptime(date_val, '%Y-%m-%d')
                except ValueError:
                    return min_datetime_for_sorting  # Fallback for unparsable strings
        return min_datetime_for_sorting  # Fallback for other types or None

    records_for_template.sort(key=get_sortable_date, reverse=True)

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
