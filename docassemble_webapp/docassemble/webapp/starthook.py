import sys
import docassemble.base.config

if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)
    sys.exit(0)
