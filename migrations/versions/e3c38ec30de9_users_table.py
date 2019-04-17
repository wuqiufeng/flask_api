"""users table

Revision ID: e3c38ec30de9
Revises: 
Create Date: 2019-04-16 21:13:55.181554

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3c38ec30de9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('active', sa.SmallInteger(), nullable=False))
    op.add_column('user', sa.Column('super', sa.SmallInteger(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'super')
    op.drop_column('user', 'active')
    # ### end Alembic commands ###
