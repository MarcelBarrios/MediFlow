from flask import Blueprint, render_template

base_bp = Blueprint('base', __name__, template_folder='../templates')

@base_bp.route("/")
def base():
    return render_template("base.html")