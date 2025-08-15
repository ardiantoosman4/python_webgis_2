# python_webgis_2
WebGIS course with Flask and Folium (part 2)

# 1) Create & activate venv
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Create .env
cp .env.example .env
# -> set DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY

# 4) Prepare database
python create_db.py

# 5) Run migrations
alembic init alembic

# 6) Adust alembic env to accept database url

# 7) Run migrations
alembic upgrade head

# 8) Add migration
alembic revision -m "some message"   

# 9) Start the app
python run.py
# visit http://localhost:5000
