from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
    jwt_required,
)
from .db import get_session
from .models.User import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.get("/register")
def register_get():
    return render_template("register.html")

@auth_bp.post("/register")
def register_post():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    if not email or not password:
        flash("Email and password are required.", "error")
        return redirect(url_for("auth.register_get"))

    session = get_session()
    try:
        user = User(email=email, password_hash=generate_password_hash(password))
        session.add(user)
        session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login_get"))
    except IntegrityError:
        session.rollback()
        flash("Email already registered.", "error")
        return redirect(url_for("auth.register_get"))

@auth_bp.get("/login")
def login_get():
    return render_template("login.html")

@auth_bp.post("/login")
def login_post():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    session = get_session()
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        flash("Invalid credentials.", "error")
        return redirect(url_for("auth.login_get"))
    
    access_token = create_access_token(identity=str(user.id))

    resp = make_response(redirect(url_for("views.dashboard")))
    set_access_cookies(resp, access_token)  # HttpOnly cookie
    return resp

@auth_bp.post("/logout")
@jwt_required()
def logout_post():
    resp = make_response(redirect(url_for("auth.login_get")))
    unset_jwt_cookies(resp)
    flash("Logged out.", "info")
    return resp
