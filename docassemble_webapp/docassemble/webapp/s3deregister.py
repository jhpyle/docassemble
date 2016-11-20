import os
import sys
import re
if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)

def main():
    from docassemble.base.config import hostname, S3_ENABLED, s3_config
    roles = os.environ.get('CONTAINERROLE', None)
    if S3_ENABLED and roles is not None:
        import docassemble.webapp.amazon
        s3 = docassemble.webapp.amazon.s3object(s3_config)
        roles = re.sub(r'^:+|:+$', r'', roles)
        role_list = roles.split(":")
        if 'all' in role_list:
            role_list = ['sql', 'redis', 'rabbitmq']
        for role in role_list:
            if role in ['sql', 'log', 'redis', 'rabbitmq']:
                key = s3.get_key('hostname-' + role)
                if key.exists():
                    key.delete()
                if role == 'rabbitmq':
                    key_two = s3.get_key('ip-rabbitmq')
                    if key_two.exists():
                        key_two.delete()

if __name__ == "__main__":
    main()
