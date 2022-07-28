import sys
import os
import re
separator = re.compile(r' *[,;] *')

if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)
    from docassemble.base.config import daconfig, parse_redis_uri
    if 'timezone' in daconfig and daconfig['timezone'] is not None:
        print('export TIMEZONE="' + str(daconfig['timezone']) + '"')
    if 'os locale' in daconfig and daconfig['os locale'] is not None:
        print('export LOCALE="' + str(daconfig['os locale']) + '"')
    else:
        print('export LOCALE="en_US.UTF-8 UTF-8"')
    if 'web server' in daconfig and isinstance(daconfig['web server'], str):
        print('export DAWEBSERVER="' + daconfig['web server'] + '"')
    else:
        print('export DAWEBSERVER="nginx"')
    if '--limited' in sys.argv:
        sys.exit(0)
    if 'other os locales' in daconfig and type(daconfig['other os locales']) is list:
        print('declare -a OTHERLOCALES')
        print('export OTHERLOCALES')
        indexno = 0
        for locale in daconfig['other os locales']:
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
    max_content_length = daconfig.get('maximum content length', 16 * 1024 * 1024)
    if isinstance(max_content_length, (int, type(None))):
        if max_content_length is None or max_content_length <= 0:
            print('export DAMAXCONTENTLENGTH=0')
        else:
            print('export DAMAXCONTENTLENGTH=' + str(max_content_length))
    else:
        print('DAMAXCONTENTLENGTH=' + str(16 * 1024 * 1024))
    if 'celery processes' in daconfig and isinstance(daconfig['celery processes'], int):
        print('DACELERYWORKERS=' + str(daconfig['celery processes']))
    if 'debian packages' in daconfig and isinstance(daconfig['debian packages'], list):
        print('declare -a PACKAGES')
        print('export PACKAGES')
        indexno = 0
        for package in daconfig['debian packages']:
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
    if 'python packages' in daconfig and type(daconfig['python packages']) is list:
        print('declare -a PYTHONPACKAGES')
        print('export PYTHONPACKAGES')
        indexno = 0
        for package in daconfig['python packages']:
            print('PYTHONPACKAGES[' + str(indexno) + ']=' + repr(str(package)))
            indexno += 1
    else:
        packages_variable = os.getenv('PYTHONPACKAGES', None)
        if packages_variable is not None and packages_variable != 'null':
            print('declare -a PYTHONPACKAGES')
            print('export PYTHONPACKAGES')
            indexno = 0
            for package in map(lambda x: x.strip(), separator.split(packages_variable)):
                print('PYTHONPACKAGES[' + str(indexno) + ']=' + repr(str(package)))
                indexno += 1
    if 'db' in daconfig:
        if 'prefix' in daconfig['db'] and daconfig['db']['prefix'] is not None:
            if daconfig['db']['prefix'].startswith('postgresql'):
                print('export DBTYPE="postgresql"')
            elif daconfig['db']['prefix'].startswith('mysql'):
                print('export DBTYPE="mysql"')
            else:
                print('export DBTYPE="other"')
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
        if 'table prefix' in daconfig['db'] and daconfig['db']['table prefix'] is not None:
            print('export DBTABLEPREFIX="' + str(daconfig['db']['table prefix']) + '"')
        if 'backup' in daconfig['db'] and daconfig['db']['backup'] is not None:
            print('export DBBACKUP="' + ('true' if daconfig['db']['backup'] else 'false') + '"')
        if 'ssl mode' in daconfig['db'] and daconfig['db']['ssl mode'] is not None:
            print('export DBSSLMODE="' + str(daconfig['db']['ssl mode']) + '"')
        if 'ssl cert' in daconfig['db'] and daconfig['db']['ssl cert'] is not None:
            print('export DBSSLCERT="' + str(daconfig['db']['ssl cert']) + '"')
        if 'ssl key' in daconfig['db'] and daconfig['db']['ssl key'] is not None:
            print('export DBSSLKEY="' + str(daconfig['db']['ssl key']) + '"')
        if 'ssl root cert' in daconfig['db'] and daconfig['db']['ssl root cert'] is not None:
            print('export DBSSLROOTCERT="' + str(daconfig['db']['ssl root cert']) + '"')
    if daconfig['supervisor'].get('username', None):
        print('export DASUPERVISORUSERNAME=' + str(daconfig['supervisor']['username']))
        print('export DASUPERVISORPASSWORD=' + str(daconfig['supervisor']['password']))
        print('export DASUPERVISOROPTS="--username ' + str(daconfig['supervisor']['username']) + ' --password ' + str(daconfig['supervisor']['password']) + ' "')
    else:
        print('export DASUPERVISORUSERNAME=""')
        print('export DASUPERVISORPASSWORD=""')
        print('export DASUPERVISOROPTS=""')
    if 'update on start' in daconfig:
        if daconfig['update on start'] is False:
            print('export DAUPDATEONSTART=false')
        elif daconfig['update on start'] == 'initial':
            print('export DAUPDATEONSTART=initial')
    if 'allow updates' in daconfig and daconfig['allow updates'] is False:
        print('export DAALLOWUPDATES=false')
    if 'allow configuration editing' in daconfig and daconfig['allow configuration editing'] is False:
        print('export DAALLOWCONFIGURATIONEDITING=false')
    if 'enable playground' in daconfig and daconfig['enable playground'] is False:
        print('export DAENABLEPLAYGROUND=false')
    if 'allow log viewing' in daconfig and daconfig['allow log viewing'] is False:
        print('export DAALLOWLOGVIEWING=false')
    if 'root owned' in daconfig and daconfig['root owned'] is True:
        print('export DAROOTOWNED=true')
    if 'read only file system' in daconfig and daconfig['read only file system'] is True:
        print('export DAREADONLYFILESYSTEM=true')
    if 'expose websockets' in daconfig and daconfig['expose websockets']:
        print('export DAEXPOSEWEBSOCKETS=true')
    if 'websockets ip' in daconfig and daconfig['websockets ip']:
        print('export DAWEBSOCKETSIP="' + str(daconfig['websockets ip']) + '"')
    if 'http port' in daconfig and daconfig['http port']:
        print('export PORT="' + str(daconfig['http port']) + '"')
    if 'stable version' in daconfig and daconfig['stable version']:
        print('export DASTABLEVERSION=true')
    if 'nginx ssl protocols' in daconfig and daconfig['nginx ssl protocols']:
        print('export DASSLPROTOCOLS=' + str(daconfig['nginx ssl protocols']))
    if 'websockets port' in daconfig and daconfig['websockets port']:
        print('export DAWEBSOCKETSPORT=' + str(daconfig['websockets port']))
    else:
        print('export DAWEBSOCKETSPORT=5000')
    if 'redis' in daconfig and daconfig['redis'] is not None:
        print('export REDIS="' + str(daconfig['redis']) + '"')
        (redis_host, redis_port, redis_username, redis_password, redis_offset, redis_cli, ssl_opts) = parse_redis_uri()
        print('export REDISCLI="' + str(redis_cli) + '"')
    if 'rabbitmq' in daconfig and daconfig['rabbitmq'] is not None:
        print('export RABBITMQ="' + str(daconfig['rabbitmq']) + '"')
    if 'backup days' in daconfig:
        try:
            days = int(daconfig['backup days'])
            assert days >= 0
        except:
            days = 14
        print('export DABACKUPDAYS="' + str(days) + '"')
    else:
        print('export DABACKUPDAYS="14"')
    if 'backup file storage' in daconfig and not daconfig['backup file storage']:
        print('export BACKUPFILESTORAGE=false')
    else:
        print('export BACKUPFILESTORAGE=true')
    if 'enable unoconv' in daconfig and daconfig['enable unoconv'] is True:
        print('export ENABLEUNOCONV=true')
    else:
        print('export ENABLEUNOCONV=false')
    if 's3' in daconfig:
        s4_options = []
        if ('enable' in daconfig['s3'] and daconfig['s3']['enable']) or ('enable' not in daconfig['s3'] and 'bucket' in daconfig['s3'] and daconfig['s3']['bucket'] is not None):
            print('export S3ENABLE=true')
        else:
            print('export S3ENABLE=false')
        if 'access key id' in daconfig['s3'] and daconfig['s3']['access key id'] is not None:
            print('export S3ACCESSKEY="' + str(daconfig['s3']['access key id']) + '"')
            print('export AWS_ACCESS_KEY_ID="' + str(daconfig['s3']['access key id']) + '"')
            print('export S3_ACCESS_KEY="' + str(daconfig['s3']['access key id']) + '"')
        if 'secret access key' in daconfig['s3'] and daconfig['s3']['secret access key'] is not None:
            print('export S3SECRETACCESSKEY="' + str(daconfig['s3']['secret access key']) + '"')
            print('export AWS_SECRET_ACCESS_KEY="' + str(daconfig['s3']['secret access key']) + '"')
            print('export S3_SECRET_KEY="' + str(daconfig['s3']['secret access key']) + '"')
        if 'bucket' in daconfig['s3'] and daconfig['s3']['bucket'] is not None:
            print('export S3BUCKET="' + str(daconfig['s3']['bucket']) + '"')
        if 'region' in daconfig['s3'] and daconfig['s3']['region'] is not None:
            print('export S3REGION="' + str(daconfig['s3']['region']) + '"')
            print('export AWS_DEFAULT_REGION="' + str(daconfig['s3']['region']) + '"')
        if 'endpoint url' in daconfig['s3'] and daconfig['s3']['endpoint url'] is not None:
            print('export S3ENDPOINTURL="' + str(daconfig['s3']['endpoint url']) + '"')
            s4_options.append('--endpoint-url=\\"' + str(daconfig['s3']['endpoint url']) + '\\"')
        if 'server side encryption' in daconfig['s3'] and isinstance(daconfig['s3']['server side encryption'], dict):
            if 'algorithm' in daconfig['s3']['server side encryption'] and daconfig['s3']['server side encryption']['algorithm'] is not None:
                print('export S3_SSE_ALGORITHM="' + str(daconfig['s3']['server side encryption']['algorithm']).strip() + '"')
                s4_options.append('--API-ServerSideEncryption=\\"' + str(daconfig['s3']['server side encryption']['algorithm']).strip() + '\\"')
            if 'customer algorithm' in daconfig['s3']['server side encryption'] and daconfig['s3']['server side encryption']['customer algorithm'] is not None:
                print('export S3_SSE_CUSTOMER_ALGORITHM="' + str(daconfig['s3']['server side encryption']['customer algorithm']).strip() + '"')
                s4_options.append('--API-SSECustomerAlgorithm=\\"' + str(daconfig['s3']['server side encryption']['customer algorithm']).strip() + '\\"')
            if 'customer key' in daconfig['s3']['server side encryption'] and daconfig['s3']['server side encryption']['customer key'] is not None:
                print('export S3_SSE_CUSTOMER_KEY="' + str(daconfig['s3']['server side encryption']['customer key']).strip() + '"')
                s4_options.append('--API-SSECustomerKey=\\"' + str(daconfig['s3']['server side encryption']['customer key']).strip() + '\\"')
            if 'KMS key ID' in daconfig['s3']['server side encryption'] and daconfig['s3']['server side encryption']['KMS key ID'] is not None:
                print('export S3_SSE_KMS_KEY_ID="' + str(daconfig['s3']['server side encryption']['KMS key ID']).strip() + '"')
                s4_options.append('--API-SSEKMSKeyId=\\"' + str(daconfig['s3']['server side encryption']['KMS key ID']).strip() + '\\"')
        if len(s4_options) > 0:
            print('export S4CMD_OPTS="' + " ".join(s4_options) + '"')
    if 'azure' in daconfig:
        if ('enable' in daconfig['azure'] and daconfig['azure']['enable']) or ('enable' not in daconfig['azure'] and 'container' in daconfig['azure'] and daconfig['azure']['container'] is not None and 'account name' in daconfig['azure'] and daconfig['azure']['account name'] is not None):
            print('export AZUREENABLE=true')
            print('export AZURE_STORAGE_KEY="' + str(daconfig['azure'].get('account key', '')) + '"')
            print('export AZURE_STORAGE_ACCOUNT="' + str(daconfig['azure']['account name']) + '"')
            print('export AZURE_STORAGE_AUTH_MODE=key')
        else:
            print('export AZUREENABLE=false')
        if 'connection string' in daconfig['azure'] and daconfig['azure']['connection string'] is not None:
            print('export AZURECONNECTIONSTRING="' + str(daconfig['azure']['connection string']) + '"')
        if 'account name' in daconfig['azure'] and daconfig['azure']['account name'] is not None:
            print('export AZUREACCOUNTNAME="' + str(daconfig['azure']['account name']) + '"')
        if 'account key' in daconfig['azure'] and daconfig['azure']['account key'] is not None:
            print('export AZUREACCOUNTKEY="' + str(daconfig['azure']['account key']) + '"')
        if 'container' in daconfig['azure'] and daconfig['azure']['container'] is not None:
            print('export AZURECONTAINER="' + str(daconfig['azure']['container']) + '"')
    if 'ec2' in daconfig and daconfig['ec2']:
        print('export EC2=true')
    if 'collect statistics' in daconfig and daconfig['collect statistics']:
        print('export COLLECTSTATISTICS=true')
    if 'kubernetes' in daconfig and daconfig['kubernetes']:
        print('export KUBERNETES=true')
    if 'log server' in daconfig and daconfig['log server'] is not None:
        print('export LOGSERVER="' + str(daconfig['log server']) + '"')
    if 'log' in daconfig and daconfig['log'] is not None:
        print('export LOGDIRECTORY="' + str(daconfig['log']) + '"')
    if 'use https' in daconfig and daconfig['use https']:
        print('export USEHTTPS=true')
    else:
        print('export USEHTTPS=false')
    if 'use cloud urls' in daconfig and daconfig['use cloud urls']:
        print('export USECLOUDURLS=true')
    else:
        print('export USECLOUDURLS=false')
    if 'use minio' in daconfig and daconfig['use minio']:
        print('export USEMINIO=true')
    else:
        print('export USEMINIO=false')
    if 'use lets encrypt' in daconfig and daconfig['use lets encrypt']:
        print('export USELETSENCRYPT=true')
    else:
        print('export USELETSENCRYPT=false')
    if 'behind https load balancer' in daconfig and daconfig['behind https load balancer']:
        print('export BEHINDHTTPSLOADBALANCER=true')
    else:
        print('export BEHINDHTTPSLOADBALANCER=false')
    if 'lets encrypt email' in daconfig and daconfig['lets encrypt email'] is not None:
        print('export LETSENCRYPTEMAIL="' + str(daconfig['lets encrypt email']) + '"')
    if 'external hostname' in daconfig and daconfig['external hostname'] is not None:
        print('export DAHOSTNAME="' + str(daconfig['external hostname']) + '"')
    if 'root' in daconfig and daconfig['root'] is not None:
        print('export POSTURLROOT="' + str(daconfig['root']) + '"')
        print('export WSGIROOT="' + str(re.sub(r'^(.+)/$', r'\1', daconfig['root'])) + '"')
    else:
        print('export POSTURLROOT="/"')
        print('export WSGIROOT="/"')
    if 'server administrator email' in daconfig and daconfig['server administrator email']:
        print('export SERVERADMIN="' + str(daconfig['server administrator email']) + '"')
    else:
        print('export SERVERADMIN="webmaster@localhost"')
    if 'web server timeout' in daconfig and daconfig['web server timeout'] is not None:
        print('export DATIMEOUT="' + str(daconfig['web server timeout']) + '"')
    if 'pip index url' in daconfig and daconfig['pip index url'] is not None and daconfig['pip index url'] != '':
        print('export PIPINDEXURL="' + str(daconfig['pip index url']) + '"')
    if 'pip extra index urls' in daconfig and daconfig['pip extra index urls'] is not None and daconfig['pip extra index urls'] != '':
        print('export PIPEXTRAINDEXURLS="' + str(daconfig['pip extra index urls']) + '"')
    sys.exit(0)
