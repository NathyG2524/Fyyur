"""empty message

Revision ID: 38ac2a95399d
Revises: 35355c3a2165
Create Date: 2022-05-31 14:31:16.717599

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '38ac2a95399d'
down_revision = '35355c3a2165'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Shows', sa.Column('start_time', sa.DateTime(), nullable=False))
    op.drop_column('Shows', 'start_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Shows', sa.Column('start_id', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.drop_column('Shows', 'start_time')
    # ### end Alembic commands ###
