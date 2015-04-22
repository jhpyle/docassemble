from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.packages.models import Package, PackageAuth
from docassemble.webapp.users.models import User, UserAuth, Role, UserRoles, UserDict, Attachments, Uploads, KVStore, Ticket, TicketNote
import docassemble.webapp.database
import psycopg2

from sqlalchemy import create_engine, MetaData

app.config['SQLALCHEMY_DATABASE_URI'] = docassemble.webapp.database.alchemy_connection_string()

def create_tables():
    db.create_all()
    return

def cleanup_permissions():
    connect_string = docassemble.webapp.database.connection_string()
    conn = psycopg2.connect(connect_string)
    cur = conn.cursor()
    cur.execute('grant all on "package" to "www-data"')
    cur.execute('grant all on "package_auth" to "www-data"')
    cur.execute('grant all on "package_id_seq" to "www-data"')
    cur.execute('grant all on "package_auth_id_seq" to "www-data"')
    cur.execute('grant all on "user" to "www-data"')
    cur.execute('grant all on "user_id_seq" to "www-data"')
    cur.execute('grant all on "user_auth" to "www-data"')
    cur.execute('grant all on "user_auth_id_seq" to "www-data"')
    conn.commit()
    return

if __name__ == "__main__":
    create_tables()
