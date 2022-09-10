"""add a column for the VoiceRSS voice

Revision ID: fd1547c94c46
Revises: a8746ddab8cb
Create Date: 2022-08-30 09:09:06.028272

"""
from alembic import op
import sqlalchemy as sa
from docassemble.webapp.database import dbtableprefix


# revision identifiers, used by Alembic.
revision = 'fd1547c94c46'
down_revision = 'a8746ddab8cb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(dbtableprefix + 'speaklist', sa.Column('voice', sa.String(20)))


def downgrade():
    op.drop_column(dbtableprefix + 'speaklist', 'voice')
