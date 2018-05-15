"""temp_user_id_to_userdictkeys

Revision ID: 66f71cf543a4
Revises: 025e06b85efc
Create Date: 2018-05-12 20:59:04.463045

"""
from alembic import op
import sqlalchemy as sa
from docassemble.webapp.database import dbtableprefix

# revision identifiers, used by Alembic.
revision = '66f71cf543a4'
down_revision = '025e06b85efc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(dbtableprefix + 'userdictkeys', sa.Column('temp_user_id', sa.Integer))


def downgrade():
    op.drop_column(dbtableprefix + 'userdictkeys', 'temp_user_id')
