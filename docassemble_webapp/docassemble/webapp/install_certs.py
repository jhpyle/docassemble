import sys
import os
import stat
import re

def main():
    from docassemble.base.config import daconfig, S3_ENABLED, s3_config
    certs_location = daconfig.get('certs', None)
    if S3_ENABLED:
        import docassemble.webapp.amazon
        s3 = docassemble.webapp.amazon.s3object(s3_config)
        bucket = None
        prefix = None
        if certs_location is None:
            bucket = s3.bucket
            prefix = 'certs'
        else:
            m = re.search(r'^s3://([^/]+)/(.*)', certs_location)
            if m:
                bucket = s3.conn.get_bucket(m.group(1))
                prefix = m.group(2)
        if bucket is not None and prefix is not None:
            if not re.search(r'/$', prefix):
                prefix = prefix + '/'
            dest = daconfig.get('cert_install_directory', '/etc/ssl/docassemble')
            if dest:
                if not os.path.isdir(dest):
                    os.makedirs(dest)
                for key in bucket.list(prefix=prefix, delimiter='/'):
                    filename = re.sub(r'.*/', '', key.name)
                    fullpath = os.path.join(dest, filename)
                    sys.stderr.write("install_certs: saving " + str(key.name) + " to " + str(fullpath) + "\n")
                    key.get_contents_to_filename(fullpath)
                    os.chmod(fullpath, stat.S_IRUSR)
            else:
                sys.stderr.write("SSL destination directory not known")
                sys.exit(1)
            return
    if certs_location is None:
        if os.path.isdir('/usr/share/docassemble/certs'):
            certs_location = '/usr/share/docassemble/certs'
        else:
            return
    if not os.path.isdir(certs_location):
        sys.stderr.write("certs directory " + str(certs_location) + " does not exist")
        sys.exit(1)
    import shutil
    dest = daconfig.get('cert_install_directory', '/etc/ssl/docassemble')
    if dest:
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        shutil.copytree(certs_location, dest)
        for root, dirs, files in os.walk(dest):
            for the_file in files:
                os.chmod(os.path.join(root, the_file), stat.S_IRUSR)
    else:
        sys.stderr.write("SSL destination directory not known")
        sys.exit(1)
    return

if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)
    main()
    sys.exit(0)
