from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

views_bp = Blueprint("views", __name__)

@views_bp.get("/")
def home():
    return render_template("login.html")

@views_bp.get("/dashboard")
@jwt_required()
def dashboard():
    user = get_jwt_identity()  # dict with id & email
    return render_template("dashboard.html", user=user)
