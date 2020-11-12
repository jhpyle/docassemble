import docassemble.base.config
import docassemble.webapp.user_database
import sys

if __name__ == "__main__":
    docassemble.base.config.load()
    if len(sys.argv) > 1:
        db_config = sys.argv[1]
    else:
        db_config = 'db'
    print(docassemble.webapp.user_database.alchemy_url(db_config))
