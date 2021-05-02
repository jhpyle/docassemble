import sys
import os
import docassemble.base.config
from docassemble.base.config import daconfig

if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)

def main():
    from docassemble.base.config import daconfig
    container_role = ':' + os.environ.get('CONTAINERROLE', '') + ':'
    if ':all:' in container_role or ':cron:' in container_role:
        import redis
        from docassemble.base.config import parse_redis_uri
        (redis_host, redis_port, redis_password, redis_offset, redis_cli) = parse_redis_uri()
        r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_offset, password=redis_password)
        if r.get('da:skip_create_tables'):
            sys.stderr.write("restart: skipping create_tables\n")
            r.delete('da:skip_create_tables')
        else:
            import docassemble.webapp.create_tables
            docassemble.webapp.create_tables.main()
        if ':cron:' in container_role:
            r.delete('da:cron_restart')

    webapp_path = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
    import docassemble.webapp.cloud
    cloud = docassemble.webapp.cloud.get_cloud()
    if cloud is not None:
        key = cloud.get_key('config.yml')
        if key.does_exist:
            key.get_contents_to_filename(daconfig['config file'])
            sys.stderr.write("Wrote config file based on copy on cloud\n")
    wsgi_file = webapp_path
    if os.path.isfile(wsgi_file):
        with open(wsgi_file, 'a'):
            os.utime(wsgi_file, None)
            sys.stderr.write("Restarted.\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
