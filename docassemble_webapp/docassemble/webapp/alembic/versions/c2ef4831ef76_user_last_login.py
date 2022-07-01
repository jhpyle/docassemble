"""user last login

Revision ID: c2ef4831ef76
Revises: 9be372ec38bc
Create Date: 2020-02-23 13:36:17.439014

"""
from alembic import op
import sqlalchemy as sa
from docassemble.webapp.database import dbtableprefix

# revision identifiers, used by Alembic.
revision = 'c2ef4831ef76'
down_revision = '9be372ec38bc'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column(dbtableprefix + 'user', sa.Column('last_login', sa.DateTime()))

def downgrade():
    op.drop_column(dbtableprefix + 'user', 'last_login')
