import sys

def main():
    import docassemble.webapp.cloud
    cloud = docassemble.webapp.cloud.get_cloud()
    if len(sys.argv) > 1:
        prefix = sys.argv[1]
    else:
        prefix = None
    recursive_list(cloud, prefix)

def recursive_list(cloud, prefix):
    for key in cloud.list_keys(prefix):
        if key.name.endswith('/'):
            recursive_list(cloud, key.name)
        else:
            print key.name

if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load()
    main()
    sys.exit(0)
