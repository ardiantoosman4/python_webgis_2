from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = "0003_create_posts_table"
down_revision = "0002_enable_postgis_extension"
branch_labels = None
depends_on = "0002_enable_postgis_extension"

def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("photo", sa.String(length=255), nullable=False),
        sa.Column("like", sa.Integer, default=0),
        sa.Column("dislike", sa.Integer, default=0),
        sa.Column("location", Geometry("POINT", srid=4326), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("posts")
