import os
from flask import Blueprint, request, render_template, redirect, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
import folium
from folium.plugins import BeautifyIcon
from .db import get_session
from .models.Post import Post
from sqlalchemy.orm import Session
from sqlalchemy import func

CATEGORY_STYLE = {
    "restaurant": {"icon": "cutlery", "color": "red"},
    "live_music": {"icon": "music", "color": "blue"},
    "art": {"icon": "paint-brush", "color": "green"},
}

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
@jwt_required()
def dashboard():
    user = get_jwt_identity()  # dict with id & email
    session = get_session()
    try:
        m = folium.Map(location=[-6.2, 106.8], zoom_start=12)
        # Fetch user-specific data for the dashboard
        posts = session.query(Post).all()
        for post in posts:
            lon, lat = session.scalar(func.ST_X(post.location)), session.scalar(func.ST_Y(post.location))

            popup_html = f"""
            <div class="card" style="width: 320px;">
                <div class="d-flex flex-column">
                    <img src="{post.photo}" class="img-fluid rounded-start" alt="{post.name}">
                    <div class="card-body p-2">
                        <h6 class="card-title mb-1">{post.name}</h6>
                        <p class="card-text mb-1"><small class="text-muted">{post.category}</small></p>
                        <p class="card-text" id="desc-{post.id}">{post.description}</p>
                        <p class="mb-0">👍 {post.like} | 👎 {post.dislike}</p>
                    </div>
                </div>
            </div>
            """

            style = CATEGORY_STYLE.get(post.category.lower(), {"icon": "info-sign", "color": "gray"})
            marker_icon = BeautifyIcon(
                icon=style["icon"],
                icon_shape="marker",
                background_color=style["color"],
                text_color="white"
            )

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=post.name,
                icon=marker_icon
            ).add_to(m)
    except Exception as e:
        print("Error fetching user data:", repr(e))
        return redirect(url_for("auth.login_get"))
    

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
    m.save(f"{current_app.static_folder}/dashboard.html")

    return render_template(
        "dashboard.html",
        filters=filters,
        ranges={
            "min_latitude": -90, "max_latitude": 90,
            "min_longitude": -180, "max_longitude": 180,
        },
        categories=[
            {"id": "art", "name": "Art"},
            {"id": "restaurant", "name": "Restaurant"},
            {"id": "live_music", "name": "Live Music"},
        ],
        user=user
    )
