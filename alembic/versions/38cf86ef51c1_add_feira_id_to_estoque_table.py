"""add_feira_id_to_estoque_table

Revision ID: 38cf86ef51c1
Revises: 5819e9f576ba
Create Date: 2025-06-01 19:38:28.738001

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38cf86ef51c1'
down_revision: Union[str, None] = '5819e9f576ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
