from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

views_bp = Blueprint("views", __name__)

@views_bp.get("/")
def home():
    try:
        # Check if JWT exists and is valid
        verify_jwt_in_request(optional=True)
        user = get_jwt_identity()
        if user:
            # User logged in, redirect to dashboard
            return redirect(url_for("views.dashboard"))
    except Exception:
        user = None
    # User not logged in
    return redirect(url_for("auth.login_get"))

@views_bp.get("/dashboard")
@jwt_required()
def dashboard():
    user = get_jwt_identity()  # dict with id & email
    return render_template("dashboard.html", user=user)
