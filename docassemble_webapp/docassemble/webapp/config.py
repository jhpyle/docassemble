import yaml

daconfig = dict()

def load(**kwargs):
    global daconfig
    filename = kwargs.get('filename', '/etc/docassemble/config.yml')
    daconfig = yaml.load(open(filename, 'r').read())
    return
