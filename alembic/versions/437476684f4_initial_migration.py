"""Initial migration

Revision ID: 437476684f4
Revises: 
Create Date: 2015-06-20 21:44:15.139839

"""

# revision identifiers, used by Alembic.
revision = '437476684f4'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('referral_conversion', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_unique_constraint(None, 'referral_conversion', ['user_id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'referral_conversion', type_='unique')
    op.alter_column('referral_conversion', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
