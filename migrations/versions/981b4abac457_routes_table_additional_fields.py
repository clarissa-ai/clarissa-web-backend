"""Routes table additional fields

Revision ID: 981b4abac457
Revises: 478a85cec46f
Create Date: 2020-07-01 19:16:25.266084

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '981b4abac457'
down_revision = '478a85cec46f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'route',
        sa.Column(
            'created_on',
            sa.DateTime(),
            nullable=False
        )
    )
    op.add_column(
        'route',
        sa.Column(
            'title',
            sa.String(length=200),
            nullable=False
        )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('route', 'title')
    op.drop_column('route', 'created_on')
    # ### end Alembic commands ###
