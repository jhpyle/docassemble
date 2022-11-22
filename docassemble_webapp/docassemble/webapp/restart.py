import datetime
import sys
import os
import subprocess
import redis
import docassemble.base.config
if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.config import daconfig, parse_redis_uri
from docassemble.webapp.cloud import get_cloud
from docassemble.base.logger import logmessage


def errlog(text):
    logmessage(str(datetime.datetime.now()) + " " + text)


def main():
    container_role = ':' + os.environ.get('CONTAINERROLE', '') + ':'
    errlog("checking to see if running create_tables if necessary")
    if ':all:' in container_role or ':cron:' in container_role:
        (redis_host, redis_port, redis_username, redis_password, redis_offset, redis_cli, ssl_opts) = parse_redis_uri()  # pylint: disable=unused-variable
        r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_offset, password=redis_password, username=redis_username, **ssl_opts)
        if daconfig.get('ip address ban enabled', True):
            keys_to_delete = r.keys('da:failedlogin:ip:*')
            for key_to_delete in keys_to_delete:
                try:
                    r.delete(key_to_delete.decode())
                except:
                    pass
        if r.get('da:skip_create_tables'):
            logmessage("restart: skipping create_tables")
            r.delete('da:skip_create_tables')
        else:
            errlog("running create_tables")
            subprocess.run(['python', '-m', 'docassemble.webapp.create_tables', os.getenv('DA_CONFIG_FILE', '/usr/share/docassemble/config/config.yml')], check=False)
            errlog("finished create_tables")
        if ':cron:' in container_role:
            r.delete('da:cron_restart')

    webapp_path = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
    cloud = get_cloud()
    if cloud is not None:
        key = cloud.get_key('config.yml')
        if key.does_exist:
            key.get_contents_to_filename(daconfig['config file'])
            logmessage("Wrote config file based on copy on cloud")
    wsgi_file = webapp_path
    if os.path.isfile(wsgi_file):
        errlog("touching wsgi file")
        with open(wsgi_file, 'a', encoding='utf-8'):
            os.utime(wsgi_file, None)
        errlog("Restarted.")
    sys.exit(0)

if __name__ == "__main__":
    main()
