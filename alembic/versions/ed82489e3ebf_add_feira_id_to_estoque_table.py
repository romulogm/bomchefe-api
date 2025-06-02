"""add_feira_id_to_estoque_table

Revision ID: ed82489e3ebf
Revises: 38cf86ef51c1
Create Date: 2025-06-01 19:49:03.363883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed82489e3ebf'
down_revision: Union[str, None] = '38cf86ef51c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
