"""add_feira_id_to_estoque_table

Revision ID: 5819e9f576ba
Revises: 8d89c59206ef
Create Date: 2025-06-01 19:36:13.977405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5819e9f576ba'
down_revision: Union[str, None] = '8d89c59206ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
