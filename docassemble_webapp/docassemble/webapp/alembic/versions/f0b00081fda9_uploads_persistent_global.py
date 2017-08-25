"""uploads persistent global

Revision ID: f0b00081fda9
Revises: 77e8971ffcbf
Create Date: 2017-08-24 17:06:36.121932

"""
from alembic import op
import sqlalchemy as sa
from docassemble.webapp.database import dbtableprefix

# revision identifiers, used by Alembic.
revision = 'f0b00081fda9'
down_revision = '77e8971ffcbf'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(dbtableprefix + 'uploads', sa.Column('private', sa.Boolean, server_default=sa.true()))
    op.add_column(dbtableprefix + 'uploads', sa.Column('persistent', sa.Boolean, server_default=sa.false()))

def downgrade():
    op.drop_column(dbtableprefix + 'uploads', 'private')
    op.drop_column(dbtableprefix + 'uploads', 'persistent')
