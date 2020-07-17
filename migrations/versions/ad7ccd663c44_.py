"""empty message

Revision ID: ad7ccd663c44
Revises: 510561a4cc65
Create Date: 2020-07-07 17:03:44.838374

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = 'ad7ccd663c44'
down_revision = '510561a4cc65'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'diagnosis',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column(
            'datetime',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=True
        ),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'illness',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column(
            'created_on',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=True
        ),
        sa.Column(
            'updated_on',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=True
        ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'symptom',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('illness_id', sa.Integer(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column(
            'created_on',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=True
            ),
        sa.Column(
            'updated_on',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=True
        ),
        sa.ForeignKeyConstraint(['illness_id'], ['illness.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column(
        'user',
        sa.Column('sex', sa.String(length=50), nullable=True)
    )
    sex = table('user', column('sex'))
    op.execute(sex.update().values(sex='None'))
    op.alter_column('user', 'sex', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'sex')
    op.drop_table('symptom')
    op.drop_table('illness')
    op.drop_table('diagnosis')
    # ### end Alembic commands ###
