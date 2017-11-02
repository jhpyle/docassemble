import sys
import os
import re
import docassemble.base.config

if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)

def main():
    from docassemble.base.config import daconfig
    container_role = os.environ.get('CONTAINERROLE', None)
    if container_role and re.search(r':(all|cron):', container_role):
        import docassemble.webapp.fix_postgresql_tables
        docassemble.webapp.fix_postgresql_tables.main()
        import docassemble.webapp.create_tables
        docassemble.webapp.create_tables.main()

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
