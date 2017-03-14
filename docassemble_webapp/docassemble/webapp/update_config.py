import sys
import docassemble.webapp.cloud

if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)

def check_for_config():
    from docassemble.base.config import daconfig
    cloud = docassemble.webapp.cloud.get_cloud()
    if cloud is not None:
        key = cloud.get_key('config.yml')
        if key.exists():
            key.get_contents_to_filename(daconfig['config file'])

if __name__ == "__main__":
    check_for_config()

            

