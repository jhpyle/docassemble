import sys
import docassemble.base.config
if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.config import daconfig
import docassemble.webapp.cloud


def check_for_config():
    cloud = docassemble.webapp.cloud.get_cloud()
    if cloud is not None:
        key = cloud.get_key('config.yml')
        if key.does_exist:
            key.get_contents_to_filename(daconfig['config file'])

if __name__ == "__main__":
    check_for_config()
