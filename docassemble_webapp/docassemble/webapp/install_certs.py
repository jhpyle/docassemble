import sys
import os
import stat
import re
import copy
import shutil
from pwd import getpwnam
if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.config import daconfig, S3_ENABLED, s3_config, AZURE_ENABLED, azure_config
from docassemble.base.logger import logmessage
import docassemble.base.amazon
import docassemble.base.microsoft


def main():
    certs_location = daconfig.get('certs', None)
    cloud = None
    prefix = None
    if S3_ENABLED:
        my_config = copy.deepcopy(s3_config)
        if certs_location is None:
            cloud = docassemble.base.amazon.s3object(my_config)
            prefix = 'certs/'
        else:
            m = re.search(r'^s3://([^/]+)/(.*)', certs_location)
            if m:
                prefix = m.group(2)
                my_config['bucket'] = m.group(1)
                cloud = docassemble.base.amazon.s3object(my_config)
    elif AZURE_ENABLED:
        my_config = copy.deepcopy(azure_config)
        if certs_location is None:
            prefix = 'certs/'
            cloud = docassemble.base.microsoft.azureobject(my_config)
        else:
            m = re.search(r'^blob://([^/]+)/([^/]+)/(.*)', certs_location)
            if m:
                my_config['account name'] = m.group(1)
                my_config['container'] = m.group(2)
                prefix = m.group(3)
                cloud = docassemble.base.microsoft.azureobject(my_config)
    if cloud is not None and prefix is not None:
        success = False
        if not re.search(r'/$', prefix):
            prefix = prefix + '/'
        dest = daconfig.get('cert install directory', '/etc/ssl/docassemble')
        if dest:
            if not os.path.isdir(dest):
                os.makedirs(dest)
            for key in cloud.list_keys(prefix=prefix):
                filename = re.sub(r'.*/', '', key.name)
                fullpath = os.path.join(dest, filename)
                logmessage("install_certs: saving " + str(key.name) + " to " + str(fullpath))
                key.get_contents_to_filename(fullpath)
                os.chmod(fullpath, stat.S_IRUSR)
                success = True
        else:
            logmessage("SSL destination directory not known")
            sys.exit(1)
        if success:
            return
    if certs_location is None:
        if os.path.isdir('/usr/share/docassemble/certs'):
            certs_location = '/usr/share/docassemble/certs'
        else:
            return
    if not os.path.isdir(certs_location):
        logmessage("certs directory " + str(certs_location) + " does not exist")
        sys.exit(1)
    dest = daconfig.get('cert install directory', '/etc/ssl/docassemble')
    if dest:
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        shutil.copytree(certs_location, dest)
        for root, dirs, files in os.walk(dest):  # pylint: disable=unused-variable
            for the_file in files:
                os.chmod(os.path.join(root, the_file), stat.S_IRUSR)
    else:
        logmessage("SSL destination directory not known")
        sys.exit(1)
    www_install = daconfig.get('web server certificate directory', '/var/www/.certs')
    if www_install:
        www_username = daconfig.get('web server user', 'www-data')
        www_uid = getpwnam(www_username)[2]
        www_gid = getpwnam(www_username)[3]
        if os.path.isdir(www_install):
            shutil.rmtree(www_install)
        shutil.copytree(certs_location, www_install)
        os.chown(www_install, www_uid, www_gid)
        for root, dirs, files in os.walk(www_install):
            for the_file in files:
                os.chown(os.path.join(root, the_file), www_uid, www_gid)
                os.chmod(os.path.join(root, the_file), stat.S_IRUSR)
    return

if __name__ == "__main__":
    main()
