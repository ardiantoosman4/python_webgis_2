from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = "0004_add_author_id_posts_table"
down_revision = "0003_create_posts_table"
branch_labels = None
depends_on = "0003_create_posts_table"

def upgrade():
    # add the column
    op.add_column("posts", sa.Column("author_id", sa.Integer(), nullable=False))

    # if you already have a users table, also add a foreign key constraint
    op.create_foreign_key(
        "fk_posts_author_id_users",
        source_table="posts",
        referent_table="users",
        local_cols=["author_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )


def downgrade():
    # remove foreign key first
    op.drop_constraint("fk_posts_author_id_users", "posts", type_="foreignkey")

    # drop the column
    op.drop_column("posts", "author_id")
