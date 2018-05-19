"""length_of_subdivisionfirst

Revision ID: eb61567ea005
Revises: 66f71cf543a4
Create Date: 2018-05-15 22:24:27.212164

"""
from alembic import op
import sqlalchemy as sa
from docassemble.webapp.database import dbtableprefix


# revision identifiers, used by Alembic.
revision = 'eb61567ea005'
down_revision = '66f71cf543a4'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(dbtableprefix + 'user', 'subdivisionfirst',
                    existing_type=sa.String(length=3),
                    type_=sa.String(length=255),
                    existing_nullable=True)
    op.alter_column(dbtableprefix + 'user', 'country',
                    existing_type=sa.String(length=2),
                    type_=sa.String(length=3),
                    existing_nullable=True)


def downgrade():
    op.alter_column(dbtableprefix + 'user', 'subdivisionfirst',
                    existing_type=sa.String(length=255),
                    type_=sa.String(length=3),
                    existing_nullable=True)
    op.alter_column(dbtableprefix + 'user', 'country',
                    existing_type=sa.String(length=3),
                    type_=sa.String(length=2),
                    existing_nullable=True)
