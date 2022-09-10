"""alter database for mysql compatibility

Revision ID: 9be372ec38bc
Revises: 4328f2c08f05
Create Date: 2020-02-16 15:43:35.276655

"""
import sys
from alembic import op
import sqlalchemy as sa
from docassemble.webapp.database import dbtableprefix, dbprefix, daconfig

# revision identifiers, used by Alembic.
revision = '9be372ec38bc'
down_revision = '4328f2c08f05'
branch_labels = None
depends_on = None


def upgrade():
    if dbprefix.startswith('postgresql') and not daconfig.get('force text to varchar upgrade', False):
        sys.stderr.write("Not changing text type to varchar type because underlying database is PostgreSQL\n")
    else:
        op.alter_column(
            table_name='userdict',
            column_name='filename',
            type_=sa.String(255)
        )
        op.alter_column(
            table_name='userdictkeys',
            column_name='filename',
            type_=sa.String(255)
        )
        op.alter_column(
            table_name='chatlog',
            column_name='filename',
            type_=sa.String(255)
        )
        op.alter_column(
            table_name='uploads',
            column_name='filename',
            type_=sa.String(255)
        )
        op.alter_column(
            table_name='uploads',
            column_name='yamlfile',
            type_=sa.String(255)
        )
        op.alter_column(
            table_name='objectstorage',
            column_name='key',
            type_=sa.String(1024)
        )
        op.alter_column(
            table_name='speaklist',
            column_name='filename',
            type_=sa.String(255)
        )
        op.alter_column(
            table_name='shortener',
            column_name='filename',
            type_=sa.String(255)
        )
        op.alter_column(
            table_name='shortener',
            column_name='key',
            type_=sa.String(255)
        )
        op.alter_column(
            table_name='machinelearning',
            column_name='key',
            type_=sa.String(1024)
        )
        op.alter_column(
            table_name='machinelearning',
            column_name='group_id',
            type_=sa.String(1024)
        )
        op.alter_column(
            table_name='globalobjectstorage',
            column_name='key',
            type_=sa.String(1024)
        )
    op.create_index(dbtableprefix + 'ix_uploads_yamlfile', 'uploads', ['yamlfile'])


def downgrade():
    op.alter_column(
        table_name='userdict',
        column_name='filename',
        type_=sa.Text()
    )
    op.alter_column(
        table_name='userdictkeys',
        column_name='filename',
        type_=sa.Text()
    )
    op.alter_column(
        table_name='chatlog',
        column_name='filename',
        type_=sa.Text()
    )
    op.alter_column(
        table_name='uploads',
        column_name='filename',
        type_=sa.Text()
    )
    op.alter_column(
        table_name='uploads',
        column_name='yamlfile',
        type_=sa.Text()
    )
    op.alter_column(
        table_name='objectstorage',
        column_name='key',
        type_=sa.Text()
    )
    op.alter_column(
        table_name='speaklist',
        column_name='filename',
        type_=sa.Text()
    )
    op.alter_column(
        table_name='shortener',
        column_name='filename',
        type_=sa.Text()
    )
    op.alter_column(
        table_name='shortener',
        column_name='key',
        type_=sa.Text()
    )
    op.alter_column(
        table_name='machinelearning',
        column_name='key',
        type_=sa.Text()
    )
    op.alter_column(
        table_name='machinelearning',
        column_name='group_id',
        type_=sa.Text()
    )
    op.alter_column(
        table_name='globalobjectstorage',
        column_name='key',
        type_=sa.Text()
    )
    op.drop_index(dbtableprefix + 'ix_uploads_yamlfile', table_name='uploads')
