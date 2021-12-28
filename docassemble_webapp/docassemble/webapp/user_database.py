import os
from docassemble.base.config import daconfig
from docassemble.base.error import DAError

def alchemy_url(db_config):
    if db_config not in daconfig or (not isinstance(daconfig[db_config], dict)) or 'name' not in daconfig[db_config]:
        raise Exception("alchemy_url: missing or invalid configuration for " + db_config)
    dbuser = daconfig[db_config].get('user', None)
    dbpassword = daconfig[db_config].get('password', None)
    dbhost = daconfig[db_config].get('host', None)
    if dbhost is None and dbuser is not None:
        dbhost = 'localhost'
    dbport = daconfig[db_config].get('port', None)
    dbprefix = daconfig[db_config].get('prefix', 'postgresql+psycopg2://')
    dbname = daconfig[db_config]['name']

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

    return alchemy_connect_string

def connect_args(db_config):
    if db_config not in daconfig or (not isinstance(daconfig[db_config], dict)) or 'name' not in daconfig[db_config]:
        raise Exception("connect_args: missing or invalid configuration for " + db_config)
    alchemy_connect_args = {}
    dbprefix = daconfig[db_config].get('prefix', 'postgresql+psycopg2://')
    if dbprefix.startswith('postgres'):
        ssl_mode = daconfig[db_config].get('ssl mode', None)
        if ssl_mode in ('disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full'):
            alchemy_connect_args['sslmode'] = ssl_mode
        for local_parameter, postgres_parameter in (('ssl cert', 'sslcert'), ('ssl key', 'sslkey'), ('ssl root cert', 'sslrootcert')):
            filename = daconfig[db_config].get(local_parameter, None)
            if isinstance(filename, str):
                cert_file = os.path.join(daconfig.get('web server certificate directory', '/var/www/.certs'), filename)
                if os.path.isfile(cert_file):
                    alchemy_connect_args[postgres_parameter] = cert_file
    return alchemy_connect_args
