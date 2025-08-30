import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/flaskdb")

    # Flask-JWT-Extended
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "False").lower() == "true"  # True in production (HTTPS)
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")  # "None" for cross-site (requires HTTPS)
    JWT_ACCESS_COOKIE_NAME = "access_token_cookie"
    SUPABASE_URL = os.getenv("PROJECT_URL", None)
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", None)
    SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "photos")
