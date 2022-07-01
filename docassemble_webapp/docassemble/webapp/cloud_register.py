import os
import sys
import re
import socket
if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.config import hostname
import docassemble.webapp.cloud

def main():
    roles = os.environ.get('CONTAINERROLE', None)
    if roles is None:
        return
    cloud = docassemble.webapp.cloud.get_cloud()
    if cloud is not None:
        roles = re.sub(r'^:+|:+$', r'', roles)
        role_list = roles.split(":")
        if 'all' in role_list:
            role_list = ['sql', 'redis', 'rabbitmq']
        for role in role_list:
            if role in ['sql', 'log', 'redis', 'rabbitmq']:
                key = cloud.get_key('hostname-' + role)
                if role == 'rabbitmq':
                    key.set_contents_from_string(socket.gethostname())
                    key_two = cloud.get_key('ip-rabbitmq')
                    key_two.set_contents_from_string(socket.gethostbyname_ex(hostname)[2][0])
                else:
                    key.set_contents_from_string(hostname)

if __name__ == "__main__":
    main()
