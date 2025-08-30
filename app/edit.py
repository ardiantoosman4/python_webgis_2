import uuid
from flask import Blueprint, render_template, redirect, url_for, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from supabase import create_client
from .config import Config

print(Config.DATABASE_URL, Config.SUPABASE_URL)
supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
BUCKET = Config.SUPABASE_BUCKET

cms_bp = Blueprint("cms", __name__)

@cms_bp.get("/cms")
@jwt_required()
def cms_get():
    user = get_jwt_identity()  # dict with id & email
    print(user, 'GET /cms')
    return render_template("cms.html", user=user)

@cms_bp.post("/cms")
@jwt_required()
def cms_edit():
    user = get_jwt_identity()  # dict with id & email
    
    # handle form data
    file = request.files.get("photo")
    if file:
        try:
            file_bytes = file.read()
            content_type = file.mimetype
            filename = f"{uuid.uuid4()}_{file.filename}"
            # Upload to Supabase
            print("Uploading to Supabase:", filename)
            supabase.storage.from_(BUCKET).upload(
                filename,
                file_bytes,
                file_options={"content-type": content_type},
            )
            print("Upload successful")
            # Get public URL
            public_url = supabase.storage.from_(BUCKET).get_public_url(filename)
            print("Uploaded to Supabase:", public_url)
        except Exception as e:
            print("Error uploading to Supabase:", e)

    # ✅ after processing, redirect back to GET /cms
    return redirect(url_for("cms.cms_get"))
