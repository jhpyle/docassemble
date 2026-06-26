from docassemble.webapp.config import daconfig
from docassemble.webapp.cloud.utils import get_cloud

def check_for_config():
    cloud = get_cloud()
    if cloud is not None:
        key = cloud.get_key('config.yml')
        if key.does_exist:
            key.get_contents_to_filename(daconfig['config file'])

if __name__ == "__main__":
    check_for_config()
