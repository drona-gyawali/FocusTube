"""models.py creation

Revision ID: 2e482b524019
Revises: 30aa3f1e7c3d
Create Date: 2025-08-09 17:11:43.934743

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2e482b524019"
down_revision: Union[str, Sequence[str], None] = "30aa3f1e7c3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add video_id as nullable first
    op.add_column(
        "uploaded_links", sa.Column("video_id", sa.String(length=11), nullable=True)
    )

    # Add other columns
    op.add_column("uploaded_links", sa.Column("title", sa.String(), nullable=True))
    op.add_column("uploaded_links", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "uploaded_links", sa.Column("channel_title", sa.String(), nullable=True)
    )
    op.add_column(
        "uploaded_links", sa.Column("thumbnail_url", sa.String(), nullable=True)
    )
    op.add_column(
        "uploaded_links", sa.Column("duration_seconds", sa.Integer(), nullable=True)
    )
    op.add_column(
        "uploaded_links", sa.Column("view_count", sa.Integer(), nullable=True)
    )
    op.add_column(
        "uploaded_links", sa.Column("like_count", sa.Integer(), nullable=True)
    )
    op.add_column(
        "uploaded_links", sa.Column("comment_count", sa.Integer(), nullable=True)
    )
    op.add_column("uploaded_links", sa.Column("tags", sa.Text(), nullable=True))

    # Update existing rows to avoid NULL in video_id
    # Replace 'unknown' with a default or dummy video_id if that fits your domain
    op.execute("UPDATE uploaded_links SET video_id = 'unknown' WHERE video_id IS NULL")

    # Alter video_id to NOT NULL now that data is safe
    op.alter_column("uploaded_links", "video_id", nullable=False)

    # Create index on video_id
    op.create_index(
        op.f("ix_uploaded_links_video_id"), "uploaded_links", ["video_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_uploaded_links_video_id"), table_name="uploaded_links")
    op.drop_column("uploaded_links", "tags")
    op.drop_column("uploaded_links", "comment_count")
    op.drop_column("uploaded_links", "like_count")
    op.drop_column("uploaded_links", "view_count")
    op.drop_column("uploaded_links", "duration_seconds")
    op.drop_column("uploaded_links", "thumbnail_url")
    op.drop_column("uploaded_links", "channel_title")
    op.drop_column("uploaded_links", "description")
    op.drop_column("uploaded_links", "title")
    op.drop_column("uploaded_links", "video_id")
