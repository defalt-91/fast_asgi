"""empty message

Revision ID: da3a0c2b7759
Revises: a3d0c4085151
Create Date: 2021-11-08 23:52:40.055425

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'da3a0c2b7759'
down_revision = 'a3d0c4085151'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('token', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.TIMESTAMP(timezone=True),
               existing_nullable=True,
               existing_server_default=sa.text("timezone('utc'::text, CURRENT_TIMESTAMP)"))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('token', 'created_at',
               existing_type=sa.TIMESTAMP(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text("timezone('utc'::text, CURRENT_TIMESTAMP)"))
    # ### end Alembic commands ###