"""Fix mistake

Revision ID: 9cbd6d66dbc6
Revises: 3c347ae0530e
Create Date: 2023-11-29 11:54:26.201433

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9cbd6d66dbc6'
down_revision: Union[str, None] = '3c347ae0530e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
