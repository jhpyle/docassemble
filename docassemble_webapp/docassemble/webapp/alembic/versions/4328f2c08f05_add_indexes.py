"""add indexes

Revision ID: 4328f2c08f05
Revises: eb61567ea005
Create Date: 2019-02-05 19:23:02.744161

"""
from alembic import op
import sqlalchemy as sa
from docassemble.webapp.database import dbtableprefix


# revision identifiers, used by Alembic.
revision = '4328f2c08f05'
down_revision = 'eb61567ea005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(dbtableprefix + 'ix_attachments_filename', 'attachments', ['filename'])
    op.create_index(dbtableprefix + 'ix_attachments_key', 'attachments', ['key'])
    op.create_index(dbtableprefix + 'ix_chatlog_filename', 'chatlog', ['filename'])
    op.create_index(dbtableprefix + 'ix_chatlog_key', 'chatlog', ['key'])
    op.create_index(dbtableprefix + 'ix_machinelearning_key', 'machinelearning', ['key'])
    op.create_index(dbtableprefix + 'ix_objectstorage_key', 'objectstorage', ['key'])
    op.create_index(dbtableprefix + 'ix_role_name', 'role', ['name'])
    op.create_index(dbtableprefix + 'ix_shortener_filename', 'shortener', ['filename'])
    op.create_index(dbtableprefix + 'ix_shortener_key', 'shortener', ['key'])
    op.create_index(dbtableprefix + 'ix_speaklist_filename', 'speaklist', ['filename'])
    op.create_index(dbtableprefix + 'ix_speaklist_key', 'speaklist', ['key'])
    op.create_index(dbtableprefix + 'ix_uploads_filename', 'uploads', ['filename'])
    op.create_index(dbtableprefix + 'ix_uploads_key', 'uploads', ['key'])
    op.create_index(dbtableprefix + 'ix_user_auth_user_id', 'user_auth', ['user_id'])
    op.create_index(dbtableprefix + 'ix_user_email', 'user', ['email'])
    op.create_index(dbtableprefix + 'ix_user_roles_role_id', 'user_roles', ['role_id'])
    op.create_index(dbtableprefix + 'ix_user_roles_user_id', 'user_roles', ['user_id'])
    op.create_index(dbtableprefix + 'ix_userdict_filename', 'userdict', ['filename'])
    op.create_index(dbtableprefix + 'ix_userdict_key', 'userdict', ['key'])
    op.create_index(dbtableprefix + 'ix_userdictkeys_filename', 'userdictkeys', ['filename'])
    op.create_index(dbtableprefix + 'ix_userdictkeys_key', 'userdictkeys', ['key'])
    op.create_index(dbtableprefix + 'ix_userdictkeys_temp_user_id', 'userdictkeys', ['temp_user_id'])
    op.create_index(dbtableprefix + 'ix_userdictkeys_user_id', 'userdictkeys', ['user_id'])
    op.create_index(dbtableprefix + 'ix_userdict_key_filename', 'userdict', ['key', 'filename'])
    op.create_index(dbtableprefix + 'ix_userdictkeys_key_filename', 'userdictkeys', ['key', 'filename'])

def downgrade():
    op.drop_index(dbtableprefix + 'ix_attachments_filename', table_name='attachments')
    op.drop_index(dbtableprefix + 'ix_attachments_key', table_name='attachments')
    op.drop_index(dbtableprefix + 'ix_chatlog_filename', table_name='chatlog')
    op.drop_index(dbtableprefix + 'ix_chatlog_key', table_name='chatlog')
    op.drop_index(dbtableprefix + 'ix_machinelearning_key', table_name='machinelearning')
    op.drop_index(dbtableprefix + 'ix_objectstorage_key', table_name='objectstorage')
    op.drop_index(dbtableprefix + 'ix_role_name', table_name='role')
    op.drop_index(dbtableprefix + 'ix_shortener_filename', table_name='shortener')
    op.drop_index(dbtableprefix + 'ix_shortener_key', table_name='shortener')
    op.drop_index(dbtableprefix + 'ix_speaklist_filename', table_name='speaklist')
    op.drop_index(dbtableprefix + 'ix_speaklist_key', table_name='speaklist')
    op.drop_index(dbtableprefix + 'ix_uploads_filename', table_name='uploads')
    op.drop_index(dbtableprefix + 'ix_uploads_key', table_name='uploads')
    op.drop_index(dbtableprefix + 'ix_user_auth_user_id', table_name='user_auth')
    op.drop_index(dbtableprefix + 'ix_user_email', table_name='user')
    op.drop_index(dbtableprefix + 'ix_user_roles_role_id', table_name='user_roles')
    op.drop_index(dbtableprefix + 'ix_user_roles_user_id', table_name='user_roles')
    op.drop_index(dbtableprefix + 'ix_userdict_filename', table_name='userdict')
    op.drop_index(dbtableprefix + 'ix_userdict_key', table_name='userdict')
    op.drop_index(dbtableprefix + 'ix_userdictkeys_filename', table_name='userdictkeys')
    op.drop_index(dbtableprefix + 'ix_userdictkeys_key', table_name='userdictkeys')
    op.drop_index(dbtableprefix + 'ix_userdictkeys_temp_user_id', table_name='userdictkeys')
    op.drop_index(dbtableprefix + 'ix_userdictkeys_user_id', table_name='userdictkeys')
    op.drop_index(dbtableprefix + 'ix_userdict_key_filename', table_name='userdict')
    op.drop_index(dbtableprefix + 'ix_userdictkeys_key_filename', table_name='userdictkeys')
