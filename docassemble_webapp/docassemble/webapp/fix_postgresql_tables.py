import os
import stat
import sys
import psycopg2
import pkg_resources
import docassemble.base.config
from io import open

if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.config import daconfig

def read_in(line, target):
    col = line.split('|')
    if col[0] not in target:
        target[col[0]] = dict()
    target[col[0]][col[1]] = {'type': col[2], 'size': col[3], 'default': col[4]}

def main():
    dbconfig = daconfig.get('db', dict())
    db_prefix = dbconfig.get('prefix', 'postgresql+psycopg2://')
    if db_prefix != 'postgresql+psycopg2://':
        sys.stderr.write("fix_postgresql_tables: skipping because configured database is not PostgreSQL.\n")
        return
    db_name = dbconfig.get('name', None)
    db_host = dbconfig.get('host', None)
    db_user = dbconfig.get('user', None)
    db_password = dbconfig.get('password', None)
    db_port = dbconfig.get('port', None)
    db_table_prefix = dbconfig.get('table prefix', None)
    schema_file = dbconfig.get('schema file', None)
    if db_name is None:
        db_name = os.getenv('DBNAME', '')
    if db_name == '':
        db_name = 'docassemble'
    if db_host is None:
        db_host = os.getenv('DBHOST', '')
    if db_host == '':
        db_host = 'localhost'
    if db_user is None:
        db_user = os.getenv('DBUSER', '')
    if db_user == '':
        db_user = 'docassemble'
    if db_password is None:
        db_password = os.getenv('DBPASSWORD', '')
    if db_password == '':
        db_password = 'abc123'
    if db_port is None:
        db_port = os.getenv('DBPORT', '')
    if db_port == '':
        db_port = '5432'
    if db_table_prefix is None:
        db_table_prefix = os.getenv('DBTABLEPREFIX', '')
    if schema_file is None:
        schema_file = os.getenv('DBSCHEMAFILE', None)
        if not (schema_file and os.path.isfile(schema_file)):
            schema_file = pkg_resources.resource_filename(pkg_resources.Requirement.parse('docassemble.webapp'), "docassemble/webapp/data/db-schema.txt")

    conn = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
    cur = conn.cursor()

    try:
        cur.execute("select table_name, column_name, data_type, character_maximum_length, column_default from information_schema.columns where table_schema='public'")
    except:
        sys.exit("failed to read existing columns from database")
    
    existing_columns = dict()
    rows = cur.fetchall()
    for col in rows:
        if col[0] not in existing_columns:
            existing_columns[col[0]] = dict()
        existing_columns[col[0]][col[1]] = {'type': col[2], 'size': col[3], 'default': col[4]}

    if 'alembic_version' in existing_columns and daconfig.get('use alembic', True):
        sys.stderr.write("fix_postgresql_tables: skipping because alembic is in use.\n")
        return
    desired_columns = dict()
    with open(schema_file, 'rU') as f:
        for line in f:
            read_in(line.rstrip(), desired_columns)

    commands = list()
    if db_table_prefix + 'shortener' in existing_columns and db_table_prefix + 'email' not in existing_columns:
        commands.append("drop table if exists " + db_table_prefix + "shortener;")
    for table_name in desired_columns:
        if db_table_prefix + table_name in existing_columns:
            for column_name in desired_columns[table_name]:
                if column_name not in existing_columns[db_table_prefix + table_name]:
                    output = "alter table \"" + db_table_prefix + table_name + "\" add column \"" + column_name + "\" " + desired_columns[table_name][column_name]['type']
                    if desired_columns[table_name][column_name]['size']:
                        output += "(" + desired_columns[table_name][column_name]['size'] + ")"
                    if desired_columns[table_name][column_name]['default']:
                        output += " default " + desired_columns[table_name][column_name]['default']
                    output += ";"
                    commands.append(output)

    if len(commands):
        for command in commands:
            try:
                cur.execute(command)
            except:
                sys.exit("Failed to run: " + command)
        conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
