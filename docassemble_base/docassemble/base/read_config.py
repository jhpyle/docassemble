import sys
import os
import re
separator = re.compile(r' *[,;] *')

if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)
    from docassemble.base.config import daconfig
    if 'timezone' in daconfig and daconfig['timezone'] is not None:
        print('export TIMEZONE="' + str(daconfig['timezone']) + '"')
    if 'os locale' in daconfig and daconfig['os locale'] is not None:
        print('export LOCALE="' + str(daconfig['os locale']) + '"')
    if 'other os locales' in daconfig and type(daconfig['other os locales']) is list:
        print('declare -a OTHERLOCALES')
        print('export OTHERLOCALES')
        indexno = 0
        for locale in daconfig['other locales']:
            print('OTHERLOCALES[' + str(indexno) + ']=' + repr(str(locale)))
            indexno += 1
    else:
        other_locales_variable = os.getenv('OTHERLOCALES', None)
        if other_locales_variable is not None and other_locales_variable != 'null':
            print('declare -a OTHERLOCALES')
            print('export OTHERLOCALES')
            indexno = 0
            for locale in map(lambda x: x.strip(), separator.split(other_locales_variable)):
                print('OTHERLOCALES[' + str(indexno) + ']=' + repr(str(locale)))
                indexno += 1
    if 'packages' in daconfig and type(daconfig['packages']) is list:
        print('declare -a PACKAGES')
        print('export PACKAGES')
        indexno = 0
        for package in daconfig['packages']:
            print('PACKAGES[' + str(indexno) + ']=' + repr(str(package)))
            indexno += 1
    else:
        packages_variable = os.getenv('PACKAGES', None)
        if packages_variable is not None and packages_variable != 'null':
            print('declare -a PACKAGES')
            print('export PACKAGES')
            indexno = 0
            for package in map(lambda x: x.strip(), separator.split(packages_variable)):
                print('PACKAGES[' + str(indexno) + ']=' + repr(str(package)))
                indexno += 1
    if 'db' in daconfig:
        if 'prefix' in daconfig['db'] and daconfig['db']['prefix'] is not None:
            print('export DBPREFIX="' + str(daconfig['db']['prefix']) + '"')
        if 'name' in daconfig['db'] and daconfig['db']['name'] is not None:
            print('export DBNAME="' + str(daconfig['db']['name']) + '"')
        if 'user' in daconfig['db'] and daconfig['db']['user'] is not None:
            print('export DBUSER="' + str(daconfig['db']['user']) + '"')
        if 'password' in daconfig['db'] and daconfig['db']['password'] is not None:
            print('export DBPASSWORD="' + str(daconfig['db']['password']) + '"')
        if 'host' in daconfig['db'] and daconfig['db']['host'] is not None:
            print('export DBHOST="' + str(daconfig['db']['host']) + '"')
        if 'port' in daconfig['db'] and daconfig['db']['port'] is not None:
            print('export DBPORT="' + str(daconfig['db']['port']) + '"')
        if 'table_prefix' in daconfig['db'] and daconfig['db']['table_prefix'] is not None:
            print('export DBTABLEPREFIX="' + str(daconfig['db']['table_prefix']) + '"')
    if 'redis' in daconfig and daconfig['redis'] is not None:
        print('export REDIS="' + str(daconfig['redis']) + '"')
    if 'rabbitmq' in daconfig and daconfig['rabbitmq'] is not None:
        print('export RABBITMQ="' + str(daconfig['rabbitmq']) + '"')
    if 's3' in daconfig:
        if 'enable' in daconfig['s3'] and daconfig['s3']['enable']:
            print('export S3ENABLE=true')
        else:
            print('export S3ENABLE=false')
        if 'access_key_id' in daconfig['s3'] and daconfig['s3']['access_key_id'] is not None:
            print('export S3ACCESSKEY="' + str(daconfig['s3']['access_key_id']) + '"')
            print('export AWS_ACCESS_KEY_ID="' + str(daconfig['s3']['access_key_id']) + '"')
        if 'secret_access_key' in daconfig['s3'] and daconfig['s3']['secret_access_key'] is not None:
            print('export S3SECRETACCESSKEY="' + str(daconfig['s3']['secret_access_key']) + '"')
            print('export AWS_SECRET_ACCESS_KEY="' + str(daconfig['s3']['secret_access_key']) + '"')
        if 'bucket' in daconfig['s3'] and daconfig['s3']['bucket'] is not None:
            print('export S3BUCKET="' + str(daconfig['s3']['bucket']) + '"')
    if 'ec2' in daconfig and daconfig['ec2']:
        print('export EC2=true')
    if 'log server' in daconfig and daconfig['log server'] is not None:
        print('export LOGSERVER="' + str(daconfig['log server']) + '"')
    if 'use https' in daconfig and daconfig['use https']:
        print('export USEHTTPS=true')
    if 'use lets encrypt' in daconfig and daconfig['use lets encrypt']:
        print('export USELETSENCRYPT=true')
    if 'lets encrypt email' in daconfig and daconfig['lets encrypt email'] is not None:
        print('export LETSENCRYPTEMAIL="' + str(daconfig['lets encrypt email']) + '"')
    if 'external hostname' in daconfig and daconfig['external hostname'] is not None:
        print('export DAHOSTNAME="' + str(daconfig['external hostname']) + '"')
    sys.exit(0)
