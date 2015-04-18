from docassemble.base.error import DAError
from docassemble.webapp.config import daconfig

if not daconfig['db']:
    daconfig['db'] = dict()
dbuser = daconfig['db'].get('user', None)
dbpassword = daconfig['db'].get('password', None)
dbhost = daconfig['db'].get('host', None)
dbport = daconfig['db'].get('port', None)
dbprefix = daconfig['db'].get('prefix', None)
dbname = daconfig['db'].get('name', None)

connect_string = ""
if dbname is not None:
    connect_string += "dbname=" + dbname
else:
    raise DAError("No database name provided")
if dbuser is not None:
    connect_string += " user=" + dbuser
if dbpassword is not None:
    connect_string += " password=" + dbpassword

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
else:
    alchemy_connect_string += '@'
if dbport is not None:
    alchemy_connect_string += ':' + dbhost
if dbname is not None:
    alchemy_connect_string += "/" + dbname
else:
    raise DAError("No database name provided")

def connection_string():
    return connect_string

def alchemy_connection_string():
    return alchemy_connect_string
