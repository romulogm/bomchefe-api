"""add_data_column_to_feiras_table

Revision ID: 4a3d2b4cb1ab
Revises: 2fa787e0137e
Create Date: 2025-06-01 15:01:54.229402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a3d2b4cb1ab'
down_revision: Union[str, None] = '2fa787e0137e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
