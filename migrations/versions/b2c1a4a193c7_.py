"""empty message

Revision ID: b2c1a4a193c7
Revises: 74c10b2152eb
Create Date: 2019-10-22 22:45:36.280643

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c1a4a193c7'
down_revision = '74c10b2152eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('jobs', sa.Column('dropoff_house', sa.String(length=64), nullable=True))
    op.add_column('jobs', sa.Column('dropoff_postcode', sa.String(length=64), nullable=True))
    op.add_column('jobs', sa.Column('dropoff_road', sa.String(length=64), nullable=True))
    op.add_column('jobs', sa.Column('dropoff_village', sa.String(length=64), nullable=True))
    op.add_column('jobs', sa.Column('pickup_house', sa.String(length=64), nullable=True))
    op.add_column('jobs', sa.Column('pickup_postcode', sa.String(length=64), nullable=True))
    op.add_column('jobs', sa.Column('pickup_road', sa.String(length=64), nullable=True))
    op.add_column('jobs', sa.Column('pickup_village', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('jobs', 'pickup_village')
    op.drop_column('jobs', 'pickup_road')
    op.drop_column('jobs', 'pickup_postcode')
    op.drop_column('jobs', 'pickup_house')
    op.drop_column('jobs', 'dropoff_village')
    op.drop_column('jobs', 'dropoff_road')
    op.drop_column('jobs', 'dropoff_postcode')
    op.drop_column('jobs', 'dropoff_house')
    # ### end Alembic commands ###
