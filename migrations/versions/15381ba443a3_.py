"""empty message

Revision ID: 15381ba443a3
Revises: 
Create Date: 2024-11-13 20:58:16.510494

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15381ba443a3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('loyalties',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('discount', sa.Float(), nullable=True),
    sa.Column('created_at', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('token', sa.String(), nullable=True),
    sa.Column('verified_at', sa.Date(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('blocked_until', sa.Date(), nullable=True),
    sa.Column('failed_count', sa.Integer(), nullable=True),
    sa.Column('loyalty_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['loyalty_id'], ['loyalties.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###

    # uzpildom pradine informacija: loyalties
    op.execute("""
        INSERT INTO loyalties (id, name, discount, created_at)
        VALUES
        (1, 'Bronze', 0.0, CURRENT_TIMESTAMP),
        (2, 'Silver', 5.0, CURRENT_TIMESTAMP)
    """)    


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('loyalties')
    # ### end Alembic commands ###
