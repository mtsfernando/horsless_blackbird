"""Seed admin user

Revision ID: 6205393ff000
Revises: afd46cf4fc29
Create Date: 2026-05-20 07:08:49.527429
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6205393ff000'
down_revision: Union[str, None] = 'afd46cf4fc29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Seed the admin user if not present, or update password/admin status if already exists
    op.execute(
        "INSERT INTO users (id, email, password_hash, is_admin, created_at) "
        "VALUES ('e8f96e48-9c17-4db3-bc12-cd53a5c010a3', 'thilina.fernando9@gmail.com', "
        "'$2b$12$HMoQRCfefeyogaJHw93jceCnxrnJH6ehSJQid7n3MpqyfJFq6ZrUS', true, NOW()) "
        "ON CONFLICT (email) DO UPDATE SET "
        "password_hash = EXCLUDED.password_hash, "
        "is_admin = EXCLUDED.is_admin"
    )
    # Insert player profile linked to the admin user using a subquery to handle existing UUIDs
    op.execute(
        "INSERT INTO players (id, user_id, display_name, created_at) "
        "VALUES ("
        "  '9b1062c3-9824-436d-986c-3dc8bd75a9e3', "
        "  (SELECT id FROM users WHERE email = 'thilina.fernando9@gmail.com'), "
        "  'Thilina Fernando', "
        "  NOW()"
        ") "
        "ON CONFLICT (user_id) DO UPDATE SET "
        "display_name = EXCLUDED.display_name"
    )


def downgrade() -> None:
    """Downgrade database schema."""
    op.execute(
        "DELETE FROM players WHERE user_id = "
        "(SELECT id FROM users WHERE email = 'thilina.fernando9@gmail.com')"
    )
    op.execute("DELETE FROM users WHERE email = 'thilina.fernando9@gmail.com'")
