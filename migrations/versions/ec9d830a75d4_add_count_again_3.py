"""add count again-3

Revision ID: ec9d830a75d4
Revises: f17cf4e25cee
Create Date: 2024-05-28 20:40:43.129431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec9d830a75d4'
down_revision: Union[str, None] = 'f17cf4e25cee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('file', 'count',
                    existing_type=sa.INTEGER(),
                    nullable=True)
    op.alter_column('file', 'file_extension',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('file', 'file_extension',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('file', 'count',
                    existing_type=sa.INTEGER(),
                    nullable=True)
    # ### end Alembic commands ###
