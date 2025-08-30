from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0002_enable_postgis_extension"
down_revision = "0001_create_users_table"  # or your last migration id
branch_labels = None
depends_on = "0001_create_users_table"

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS postgis;")
