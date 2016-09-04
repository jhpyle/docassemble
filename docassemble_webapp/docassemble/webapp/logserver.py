import sys
if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)
    from docassemble.base.config import daconfig
    if 'log server' in docassemble.base.config.daconfig:
        sys.stdout.write(docassemble.base.config.daconfig['log server'])
    sys.exit(0)
