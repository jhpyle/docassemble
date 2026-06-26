import sys
import docassemble.base.config

if __name__ == "__main__":
    docassemble.base.config.load()
    import docassemble.webapp.user_database
    if len(sys.argv) > 1:
        db_config = sys.argv[1]
    else:
        db_config = 'db'  # pylint: disable=invalid-name
    print(docassemble.webapp.user_database.alchemy_url(db_config))
