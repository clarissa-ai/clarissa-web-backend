"""added birthdate to user

Revision ID: 510561a4cc65
Revises: 981b4abac457
Create Date: 2020-07-06 22:13:29.989749

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = '510561a4cc65'
down_revision = '981b4abac457'
branch_labels = None
depends_on = None


def upgrade():
    # UPDATED TO update existing users
    op.add_column('user', sa.Column('birthdate', sa.Date(), nullable=True))
    birthdate = table('user', column('birthdate'))
    op.execute(birthdate.update().values(birthdate='2000-01-01'))
    op.alter_column('user', 'birthdate', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'birthdate')
    # ### end Alembic commands ###
