"""added user followers

Revision ID: d0b8133f3d63
Revises: f3287c4f26d0
Create Date: 2018-03-29 20:58:20.947909

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0b8133f3d63'
down_revision = 'f3287c4f26d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.uid'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.uid'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_followers')
    # ### end Alembic commands ###
