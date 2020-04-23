"""add tables: records/subcribes

Revision ID: f66c30ea4587
Revises: 64eca6f7553a
Create Date: 2020-04-23 17:01:20.236094

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f66c30ea4587'
down_revision = '64eca6f7553a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat_records',
    sa.Column('create_at', sa.DateTime(), nullable=True),
    sa.Column('update_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('self_id', sa.Integer(), nullable=True),
    sa.Column('ctx_id', sa.String(length=64), nullable=True),
    sa.Column('msg', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sub_content',
    sa.Column('create_at', sa.DateTime(), nullable=True),
    sa.Column('update_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('intervel', sa.Integer(), nullable=True),
    sa.Column('link', sa.LargeBinary(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('last_update', sa.String(length=32), nullable=True),
    sa.Column('content', sa.LargeBinary(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_sub',
    sa.Column('create_at', sa.DateTime(), nullable=True),
    sa.Column('update_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('sub_id', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('only_title', sa.Boolean(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_sub')
    op.drop_table('sub_content')
    op.drop_table('chat_records')
    # ### end Alembic commands ###
