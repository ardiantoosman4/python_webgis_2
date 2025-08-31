import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from supabase import create_client
from geoalchemy2.shape import from_shape
from sqlalchemy import func
from shapely.geometry import Point
from .config import Config
from .db import get_session
from .models.Post import Post

print(Config.DATABASE_URL, Config.SUPABASE_URL)
supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
BUCKET = Config.SUPABASE_BUCKET

cms_bp = Blueprint("cms", __name__)


@cms_bp.route("/my-posts")
@jwt_required()
def my_posts_page():
    user = get_jwt_identity()  # dict with id & email
    try:
        session = get_session()
        user_id = user
        my_posts = session.query(Post).filter_by(author_id=user_id).all()
        return render_template("my_posts.html", user=user, my_posts=my_posts)
    except Exception as e:
        flash("Error fetching posts:", repr(e))

    return render_template("my_posts.html", user=user, my_posts=my_posts)

@cms_bp.route("/other-posts")
@jwt_required()
def other_posts_page():
    user = get_jwt_identity()  # dict with id & email
    try:
        session = get_session()
        user_id = user
        other_posts = session.query(Post).filter(Post.author_id != user_id).all()
        return render_template("other_posts.html", user=user, other_posts=other_posts)
    except Exception as e:
        flash("Error fetching posts:", repr(e))

    return render_template("other_posts.html", user=user, other_posts=other_posts)


# --- Actions ---
@cms_bp.route("/posts/create", methods=["GET", "POST"])
@jwt_required()
def create_post():
    user = get_jwt_identity()
    if request.method == "POST":
        session = get_session()
        author_id = user
        name = request.form.get("name")
        category = request.form.get("category")
        description = request.form.get("description")
        longitude = request.form.get("longitude")
        latitude = request.form.get("latitude")
        file = request.files.get("photo")

        if file:
            try:
                # upload photo
                file_bytes = file.read()
                content_type = file.mimetype
                filename = f"{uuid.uuid4()}_{file.filename}"
                supabase.storage.from_(BUCKET).upload(
                    filename,
                    file_bytes,
                    file_options={"content-type": content_type},
                )
                # Get public URL
                public_url = supabase.storage.from_(BUCKET).get_public_url(filename)

                post = Post(
                    author_id=author_id,
                    name=name,
                    category=category,
                    description=description,
                    photo=public_url,
                    location=from_shape(Point(longitude, latitude), srid=4326)
                )
                session.add(post)
                session.commit()
                flash("Success creating post", "success")
            except Exception as e:
                flash("Error:", e)
                session.rollback()
            finally:
                return redirect(url_for("cms.my_posts_page"))
    return render_template("create_post.html")


@cms_bp.get("/posts/edit/<int:post_id>")
@jwt_required()
def edit_post(post_id):
    user = get_jwt_identity()
    session = get_session()
    try:
        post_data  = (
            session.query(
                Post, 
                func.ST_Y(Post.location).label("latitude"),
                func.ST_X(Post.location).label("longitude")
            )
            .filter(Post.id == post_id)
            .first()
        )
        
        if not post_data:
            flash("Post not found", "danger")
            return redirect(url_for("cms.my_posts_page"))
        
        post_obj, lat, lon = post_data

        post = {
            "id": post_obj.id,
            "name": post_obj.name,
            "category": post_obj.category,
            "description": post_obj.description,
            "author_id": post_obj.author_id,
            "latitude": lat,
            "longitude": lon,
        }

        if post and str(post["author_id"]) != user:
            flash("You are not authorized to edit this post", "danger")
        else:
            return render_template("edit_post.html", post=post)
        
    except Exception as e:
        print(e)
        return redirect(url_for("cms.my_posts_page"))
    
@cms_bp.post("/posts/edit/<int:post_id>")
@jwt_required()
def edit_post_submit(post_id):
    user = get_jwt_identity()
    session = get_session()
    try:
        post = session.query(Post).filter_by(id=post_id).first()
        if post and str(post.author_id) != user:
            return redirect(url_for("cms.my_posts_page"))
        
        file = request.files.get("photo")

        longitude = request.form.get("longitude")
        latitude = request.form.get("latitude")
        updated_post = {
            "name": request.form.get("name"),
            "category": request.form.get("category"),
            "description": request.form.get("description"),
            "location": from_shape(Point(longitude, latitude), srid=4326)
        }

        if file:
            file_bytes = file.read()
            content_type = file.mimetype
            filename = f"{uuid.uuid4()}_{file.filename}"
            supabase.storage.from_(BUCKET).upload(
                filename,
                file_bytes,
                file_options={"content-type": content_type},
            )
            # Get public URL
            public_url = supabase.storage.from_(BUCKET).get_public_url(filename)
            updated_post["photo"] = public_url

        session.query(Post).filter_by(id=post_id).update(updated_post)
        session.commit()
    except Exception as e:
        print(e)
    finally:
        return redirect(url_for("cms.my_posts_page"))

@cms_bp.route("/posts/delete/<int:post_id>", methods=["POST"])
@jwt_required()
def delete_post(post_id):
    user = get_jwt_identity()
    session = get_session()
    try:
        post = session.query(Post).filter_by(id=post_id).first()
        if post and str(post.author_id) != user:
            return redirect(url_for("cms.my_posts_page"))
        if post:
            session.delete(post)
            session.commit()
    except Exception as e:
        flash("Error deleting post:", repr(e))
    return redirect(url_for("cms.my_posts_page"))


@cms_bp.route("/posts/like/<int:post_id>", methods=["POST"])
@jwt_required()
def like_post(post_id):
    user = get_jwt_identity()
    session = get_session()
    try:
        post = session.query(Post).filter_by(id=post_id).first()
        if post:
            post.like += 1
            session.commit()
    except Exception as e:
        flash("Error liking post:", repr(e))
    return redirect(url_for("cms.other_posts_page"))


@cms_bp.route("/posts/dislike/<int:post_id>", methods=["POST"])
@jwt_required()
def dislike_post(post_id):
    user = get_jwt_identity()
    session = get_session()
    try:
        post = session.query(Post).filter_by(id=post_id).first()
        if post:
            post.dislike += 1
            session.commit()
    except Exception as e:
        flash("Error disliking post:", repr(e))
    return redirect(url_for("cms.other_posts_page"))