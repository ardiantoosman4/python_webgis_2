import os
from flask import Blueprint, request, render_template, redirect, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
import folium

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

@views_bp.route("/dashboard", methods=["GET", "POST"])
@jwt_required(optional=True)
def dashboard():
    user = get_jwt_identity()  # dict with id & email

    # Handle GET or POST data
    if request.method == "POST":
        get_value = request.form.get
    else:  # GET
        get_value = request.args.get

    filters = {
        "min_rating": float(get_value("min_rating", 0)),
        "max_rating": float(get_value("max_rating", 5)),
        "category": float(get_value("category", 1)),
    }

    # Export map as HTML string
    m = folium.Map([43, -100], zoom_start=5)
    m.save(f"{current_app.static_folder}/dashboard.html")

    return render_template(
        "dashboard.html",
        filters=filters,
        ranges={
            "min_rating": 0, "max_rating": 5,
        },
        categories=[
            {"id": 1, "name": "Category 1"},
            {"id": 2, "name": "Category 2"},
            {"id": 3, "name": "Category 3"},
        ],
        user=user
    )
