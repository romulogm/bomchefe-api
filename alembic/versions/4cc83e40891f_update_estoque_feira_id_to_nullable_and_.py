"""update_estoque_feira_id_to_nullable_and_add_relationship

Revision ID: 4cc83e40891f
Revises: ed82489e3ebf
Create Date: 2025-06-01 20:14:38.034540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4cc83e40891f'
down_revision: Union[str, None] = 'ed82489e3ebf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
