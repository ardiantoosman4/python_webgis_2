import os
from flask import Blueprint, request, render_template, redirect, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
import folium
from folium.plugins import BeautifyIcon
from .db import get_session
from .models.Post import Post
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2 import Geography

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

def get_filtered_posts(session, filters):
    query = session.query(Post)

    # filter by likes
    if filters.get("min_like") is not None and filters.get("min_like") != '':
        query = query.filter(Post.like >= float(filters["min_like"]))

    # filter by dislikes
    if filters.get("max_dislike") is not None and filters.get("max_dislike") != '':
        query = query.filter(Post.dislike <= float(filters["max_dislike"]))

    # filter by category
    if filters.get("category") is not None and filters.get("category") != '':
        query = query.filter(Post.category == filters["category"])

    # filter by distance
    if (
        (filters.get("latitude") is not None and filters.get("latitude") != '') and
        (filters.get("longitude") is not None and filters.get("longitude") != '') and
        (filters.get("max_distance") is not None and filters.get("max_distance") != '')
    ):
        lat = float(filters["latitude"])
        lon = float(filters["longitude"])
        max_dist = 1000 # default 1 Km
        if filters.get("max_distance") is not None:
            max_dist = float(filters["max_distance"]) * 1000

        # reference point
        point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
        point_geog = func.ST_GeographyFromText(func.ST_AsText(point))

        query = query.filter(
            func.ST_DWithin(Post.location.cast(Geography), point_geog, max_dist)
        )

    return query.all()

@views_bp.route("/dashboard", methods=["GET", "POST"])
@jwt_required()
def dashboard():
    user = get_jwt_identity()  # dict with id & email
    session = get_session()
    m = folium.Map(location=[-6.2, 106.8], zoom_start=12)

    try:
        # Handle GET or POST data
        filters = {
            "min_like": None,
            "max_dislike": None,
            "latitude": None,
            "longitude": None,
            "max_distance": None,
            "category": None
        }

        if request.method == "POST":
            get_value = request.form.get
            filters = {
                "min_like": get_value("min_like", None),
                "max_dislike": get_value("max_dislike", None),
                "latitude": get_value("latitude", None),
                "longitude": get_value("longitude", None),
                "max_distance": get_value("max_distance", None),
                "category": get_value("category", None)
            }

        # add marker for user location
        if (
            filters["latitude"] is not None and filters["latitude"] != '' and
            filters["longitude"] is not None and filters["longitude"] != '' and
            filters["max_distance"] is not None and filters["max_distance"] != ''
        ):
            latitude = float(filters["latitude"])
            longitude = float(filters["longitude"])
            max_distance = float(filters["max_distance"]) * 1000  # convert km → meters
            folium.Circle(
                location=[latitude, longitude],
                radius=max_distance,
                color="blue",
                weight=2,
                fill=True,
                fill_opacity=0.2,
            ).add_to(m)
            folium.Marker(
                location=[latitude, longitude],
                tooltip="Your Location",
                icon=folium.Icon(icon="user", prefix="fa", color="red")
            ).add_to(m)
        

        # setup markers for posts
        posts = get_filtered_posts(session, filters)
        for post in posts:
            lon, lat = session.scalar(func.ST_X(post.location)), session.scalar(func.ST_Y(post.location))

            popup_html = f"""
            <div class="card" style="width: 320px;">
                <div class="d-flex flex-column">
                    <img src="{post.photo}" class="img-fluid rounded-start" alt="{post.name}">
                    <div class="card-body p-2">
                        <h5 class="card-title fw-bold text-dark mb-1">{ post.name }</h5>
                        <h6 class="card-subtitle mb-1">
                            <span class="badge bg-info text-dark px-2 py-1">{post.category }</span>
                            <span class="mb-0">👍 {post.like} | 👎 {post.dislike}</span>
                        </h6>
                        <p class="card-text" id="desc-{post.id}">{post.description}</p>
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
