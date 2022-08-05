import os
import docassemble.base.config
if not docassemble.base.config.loaded:
    docassemble.base.config.load()
from docassemble.base.error import DAError
from docassemble.base.config import daconfig

if 'db' not in daconfig:
    daconfig['db'] = {}
dbuser = daconfig['db'].get('user', None)
dbpassword = daconfig['db'].get('password', None)
dbhost = daconfig['db'].get('host', None)
if dbhost is None and dbuser is not None:
    dbhost = 'localhost'
dbport = daconfig['db'].get('port', None)
dbprefix = daconfig['db'].get('prefix', 'postgresql+psycopg2://')
dbname = daconfig['db'].get('name', 'docassemble')
dbtableprefix = daconfig['db'].get('table prefix', None)
if not dbtableprefix:
    dbtableprefix = ''

connect_string = ""
if dbname is not None:
    connect_string += "dbname=" + dbname
else:
    raise DAError("No database name provided")
if dbuser is not None:
    connect_string += " user=" + dbuser
if dbpassword is not None:
    connect_string += " password=" + dbpassword

pool_pre_ping = daconfig.get('sql ping', False)

alchemy_connect_string = ""
if dbprefix is not None:
    alchemy_connect_string += dbprefix
if dbuser is not None:
    alchemy_connect_string += dbuser
if dbpassword is not None:
    alchemy_connect_string += ":" + dbpassword
else:
    alchemy_connect_string += ":"
if dbhost is not None:
    alchemy_connect_string += '@' + dbhost
    if dbport is not None:
        alchemy_connect_string += ':' + str(dbport)
else:
    alchemy_connect_string += '@'
if not dbprefix.startswith('oracle'):
    if dbname is not None:
        alchemy_connect_string += "/" + dbname
    else:
        raise DAError("No database name provided")

alchemy_connect_args = {}
if alchemy_connect_string.startswith('postgres'):
    ssl_mode = daconfig['db'].get('ssl mode', None)
    if ssl_mode in ('disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full'):
        alchemy_connect_args['sslmode'] = ssl_mode
    for local_parameter, postgres_parameter in (('ssl cert', 'sslcert'), ('ssl key', 'sslkey'), ('ssl root cert', 'sslrootcert')):
        filename = daconfig['db'].get(local_parameter, None)
        if isinstance(filename, str):
            cert_file = os.path.join(daconfig.get('web server certificate directory', '/var/www/.certs'), filename)
            if os.path.isfile(cert_file):
                alchemy_connect_args[postgres_parameter] = cert_file


def connection_string():
    return connect_string


def alchemy_connection_string():
    return alchemy_connect_string


def connect_args():
    return alchemy_connect_args
