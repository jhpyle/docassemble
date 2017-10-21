import os
import sys
import re
if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)

def main():
    from docassemble.base.config import hostname
    roles = os.environ.get('CONTAINERROLE', None)
    if roles is None:
        return
    import docassemble.webapp.cloud
    cloud = docassemble.webapp.cloud.get_cloud()
    if cloud is not None:
        roles = re.sub(r'^:+|:+$', r'', roles)
        role_list = roles.split(":")
        if 'all' in role_list:
            role_list = ['sql', 'redis', 'rabbitmq']
        for role in role_list:
            if role in ['sql', 'log', 'redis', 'rabbitmq']:
                key = cloud.get_key('hostname-' + role)
                if key.does_exist:
                    key.delete()
                if role == 'rabbitmq':
                    key_two = cloud.get_key('ip-rabbitmq')
                    if key_two.does_exist:
                        key_two.delete()

if __name__ == "__main__":
    main()
