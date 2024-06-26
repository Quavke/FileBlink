"""add count again-2

Revision ID: f17cf4e25cee
Revises: acabf7d22cb4
Create Date: 2024-05-28 20:39:57.092218

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f17cf4e25cee'
down_revision: Union[str, None] = 'acabf7d22cb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('file', sa.Column('count', sa.Integer(), nullable=True))
    op.alter_column('file', 'file_extension',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('file', 'file_extension',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.drop_column('file', 'count')
    # ### end Alembic commands ###
