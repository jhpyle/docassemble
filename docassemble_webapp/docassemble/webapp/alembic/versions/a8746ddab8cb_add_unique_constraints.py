"""add unique constraints

Revision ID: a8746ddab8cb
Revises: 693d02299f38
Create Date: 2022-04-07 17:49:47.832279

"""
from alembic import op
from docassemble.webapp.database import dbtableprefix


# revision identifiers, used by Alembic.
revision = 'a8746ddab8cb'
down_revision = '693d02299f38'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(dbtableprefix + 'chatlog_id_key', dbtableprefix + 'chatlog', ['id'])
    op.create_unique_constraint(dbtableprefix + 'email_id_key', dbtableprefix + 'email', ['id'])
    op.create_unique_constraint(dbtableprefix + 'emailattachment_id_key', dbtableprefix + 'emailattachment', ['id'])
    op.create_unique_constraint(dbtableprefix + 'globalobjectstorage_id_key', dbtableprefix + 'globalobjectstorage', ['id'])
    op.create_unique_constraint(dbtableprefix + 'jsonstorage_id_key', dbtableprefix + 'jsonstorage', ['id'])
    op.create_unique_constraint(dbtableprefix + 'machinelearning_id_key', dbtableprefix + 'machinelearning', ['id'])
    op.create_unique_constraint(dbtableprefix + 'objectstorage_id_key', dbtableprefix + 'objectstorage', ['id'])
    op.create_unique_constraint(dbtableprefix + 'role_id_key', dbtableprefix + 'role', ['id'])
    op.create_unique_constraint(dbtableprefix + 'shortener_id_key', dbtableprefix + 'shortener', ['id'])
    op.create_unique_constraint(dbtableprefix + 'speaklist_id_key', dbtableprefix + 'speaklist', ['id'])
    op.create_unique_constraint(dbtableprefix + 'supervisors_id_key', dbtableprefix + 'supervisors', ['id'])
    op.create_unique_constraint(dbtableprefix + 'tempuser_id_key', dbtableprefix + 'tempuser', ['id'])
    op.create_unique_constraint(dbtableprefix + 'uploads_indexno_key', dbtableprefix + 'uploads', ['indexno'])
    op.create_unique_constraint(dbtableprefix + 'uploadsroleauth_id_key', dbtableprefix + 'uploadsroleauth', ['id'])
    op.create_unique_constraint(dbtableprefix + 'uploadsuserauth_id_key', dbtableprefix + 'uploadsuserauth', ['id'])
    op.create_unique_constraint(dbtableprefix + 'user_id_key', dbtableprefix + 'user', ['id'])
    op.create_unique_constraint(dbtableprefix + 'user_auth_id_key', dbtableprefix + 'user_auth', ['id'])
    op.create_unique_constraint(dbtableprefix + 'user_invite_id_key', dbtableprefix + 'user_invite', ['id'])
    op.create_unique_constraint(dbtableprefix + 'user_roles_id_key', dbtableprefix + 'user_roles', ['id'])


def downgrade():
    op.drop_constraint(dbtableprefix + 'chatlog_id_key', dbtableprefix + 'chatlog')
    op.drop_constraint(dbtableprefix + 'email_id_key', dbtableprefix + 'email')
    op.drop_constraint(dbtableprefix + 'emailattachment_id_key', dbtableprefix + 'emailattachment')
    op.drop_constraint(dbtableprefix + 'globalobjectstorage_id_key', dbtableprefix + 'globalobjectstorage')
    op.drop_constraint(dbtableprefix + 'jsonstorage_id_key', dbtableprefix + 'jsonstorage')
    op.drop_constraint(dbtableprefix + 'machinelearning_id_key', dbtableprefix + 'machinelearning')
    op.drop_constraint(dbtableprefix + 'objectstorage_id_key', dbtableprefix + 'objectstorage')
    op.drop_constraint(dbtableprefix + 'role_id_key', dbtableprefix + 'role')
    op.drop_constraint(dbtableprefix + 'shortener_id_key', dbtableprefix + 'shortener')
    op.drop_constraint(dbtableprefix + 'speaklist_id_key', dbtableprefix + 'speaklist')
    op.drop_constraint(dbtableprefix + 'supervisors_id_key', dbtableprefix + 'supervisors')
    op.drop_constraint(dbtableprefix + 'tempuser_id_key', dbtableprefix + 'tempuser')
    op.drop_constraint(dbtableprefix + 'uploads_indexno_key', dbtableprefix + 'uploads')
    op.drop_constraint(dbtableprefix + 'uploadsroleauth_id_key', dbtableprefix + 'uploadsroleauth')
    op.drop_constraint(dbtableprefix + 'uploadsuserauth_id_key', dbtableprefix + 'uploadsuserauth')
    op.drop_constraint(dbtableprefix + 'user_id_key', dbtableprefix + 'user')
    op.drop_constraint(dbtableprefix + 'user_auth_id_key', dbtableprefix + 'user_auth')
    op.drop_constraint(dbtableprefix + 'user_invite_id_key', dbtableprefix + 'user_invite')
    op.drop_constraint(dbtableprefix + 'user_roles_id_key', dbtableprefix + 'user_roles')
