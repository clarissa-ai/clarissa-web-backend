"""added title to illness

Revision ID: e0b018d33394
Revises: 300ca53aa7e6
Create Date: 2020-07-14 23:38:56.686371

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = 'e0b018d33394'
down_revision = '300ca53aa7e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'illness',
        sa.Column('title', sa.String(length=200), nullable=True)
    )
    birthdate = table('illness', column('title'))
    op.execute(birthdate.update().values(title='Untitled Illness'))
    op.alter_column('illness', 'title', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('illness', 'title')
    # ### end Alembic commands ###
