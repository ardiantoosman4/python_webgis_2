import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create an engine without touching Base.metadata yet
engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")

if not database_exists(engine.url):
    print(f"Database does not exist. Creating {engine.url.database}...")
    create_database(engine.url)
    print("Database created!")
else:
    print("Database already exists.")
