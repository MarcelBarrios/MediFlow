from flask import Blueprint, render_template, current_app, request, abort, redirect, url_for, flash
from bson import ObjectId
from datetime import datetime


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
    # flash("Please select a patient first.", "info")
    return redirect(url_for('all_patients.all_patients'))


@patient_bp.route("/patient/<patient_id>", methods=["GET"])
def patient_detail(patient_id):
    try:
        obj_id = ObjectId(patient_id)
    except Exception:
        abort(404, description="Invalid patient ID format.")

    patient = current_app.mongo.db.patients.find_one({"_id": obj_id})

    if not patient:
        abort(404, description="Patient not found.")

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

    all_records = patient.get("medical_records", [])
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
        record_copy["status_style"] = STATUS_STYLES.get(
            status, DEFAULT_STATUS_STYLE)
        record_copy["category_style"] = CATEGORY_STYLES.get(
            category, DEFAULT_CATEGORY_STYLE)
        record_copy["formatted_date"] = format_date(record.get("date"))
        records_for_template.append(record_copy)

    records_for_template.sort(key=lambda r: r.get("date", ""), reverse=True)

    return render_template(
        "patient.html",
        patient=patient,
        records=records_for_template,
        active_filters=filter_args
    )
