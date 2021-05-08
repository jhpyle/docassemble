"""fix indexes

Revision ID: 693d02299f38
Revises: c2ef4831ef76
Create Date: 2021-05-08 07:49:59.180288

"""
from alembic import op
import sqlalchemy as sa
from docassemble.webapp.database import dbtableprefix


# revision identifiers, used by Alembic.
revision = '693d02299f38'
down_revision = 'c2ef4831ef76'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.drop_index(dbtableprefix + 'ix_userdictkeys_key_filename', table_name='userdict')
        op.create_index(dbtableprefix + 'ix_userdictkeys_key_filename', 'userdictkeys', ['key', 'filename'])
    except:
        pass


def downgrade():
    pass
