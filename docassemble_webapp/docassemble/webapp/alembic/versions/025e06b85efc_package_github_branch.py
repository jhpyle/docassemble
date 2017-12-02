"""package github branch

Revision ID: 025e06b85efc
Revises: f0b00081fda9
Create Date: 2017-12-01 20:37:28.967575

"""
from alembic import op
import sqlalchemy as sa
from docassemble.webapp.database import dbtableprefix

# revision identifiers, used by Alembic.
revision = '025e06b85efc'
down_revision = 'f0b00081fda9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(dbtableprefix + 'package', sa.Column('gitbranch', sa.String(255)))

def downgrade():
    op.drop_column(dbtableprefix + 'package', 'gitbranch')
