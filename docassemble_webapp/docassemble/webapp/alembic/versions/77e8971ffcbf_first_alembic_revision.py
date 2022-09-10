"""first alembic revision

Revision ID: 77e8971ffcbf
Revises:
Create Date: 2017-08-13 09:07:33.368044

"""
from alembic import op
import sqlalchemy as sa
from docassemble.webapp.database import dbtableprefix

# revision identifiers, used by Alembic.
revision = '77e8971ffcbf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(dbtableprefix + 'user', sa.Column('modified_at', sa.DateTime))


def downgrade():
    op.drop_column(dbtableprefix + 'user', 'modified_at')
