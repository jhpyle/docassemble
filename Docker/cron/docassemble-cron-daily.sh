#! /bin/bash

export DA_CONFIG_FILE=/usr/share/docassemble/config/config.yml
source /usr/share/docassemble/local/bin/activate
export CONTAINERROLE=":${CONTAINERROLE:-all}:"
source /dev/stdin < <(su -c "source /usr/share/docassemble/local/bin/activate && python -m docassemble.base.read_config $DA_CONFIG_FILE" www-data)

if [ "${S3ENABLE:-null}" == "null" ] && [ "${S3BUCKET:-null}" != "null" ]; then
    export S3ENABLE=true
fi

if [ "${S3ENABLE:-null}" == "true" ] && [ "${S3BUCKET:-null}" != "null" ] && [ "${S3ACCESSKEY:-null}" != "null" ] && [ "${S3SECRETACCESSKEY:-null}" != "null" ]; then
    export AWS_ACCESS_KEY_ID=$S3ACCESSKEY
    export AWS_SECRET_ACCESS_KEY=$S3SECRETACCESSKEY
fi

if [ "${AZUREENABLE:-null}" == "null" ] && [ "${AZUREACCOUNTNAME:-null}" != "null" ] && [ "${AZURECONTAINER:-null}" != "null" ]; then
    export AZUREENABLE=true
    blob-cmd add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
fi

if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    /usr/share/docassemble/webapp/run-cron.sh cron_daily
fi

MONTHDAY=$(date +%m-%d)
BACKUPDIR=/usr/share/docassemble/backup/$MONTHDAY
rm -rf $BACKUPDIR
mkdir -p $BACKUPDIR
if [[ $CONTAINERROLE =~ .*:(all|web|celery|log|cron):.* ]]; then
    rsync -au /usr/share/docassemble/files $BACKUPDIR/
    rsync -au /usr/share/docassemble/config $BACKUPDIR/
    rsync -au --exclude '*/worker.log' /usr/share/docassemble/log $BACKUPDIR/
fi

if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]]; then
    PGBACKUPDIR=`mktemp -d`
    chown postgres.postgres "$PGBACKUPDIR"
    su postgres -c 'psql -Atc "SELECT datname FROM pg_database" postgres' | grep -v -e template -e postgres | awk -v backupdir="$PGBACKUPDIR" '{print "cd /tmp; su postgres -c \"pg_dump -F c -f " backupdir "/" $1 " " $1 "\""}' | bash
    rsync -au "$PGBACKUPDIR" $BACKUPDIR/postgres
    if [ "${S3ENABLE:-false}" == "true" ]; then
	s3cmd sync "$PGBACKUPDIR/" s3://${S3BUCKET}/postgres/
    fi
    if [ "${AZUREENABLE:-false}" == "true" ]; then
	for the_file in $( find "$PGBACKUPDIR/" -type f ); do
	    blob-cmd -f cp "$the_file" 'blob://'${AZUREACCOUNTNAME}'/'${AZURECONTAINER}"/postgres/$the_file"
	done
    fi
    rm -rf "$PGBACKUPDIR"
fi
if [ "${AZUREENABLE:-false}" == "false" ]; then
   rm -rf `find /usr/share/docassemble/backup -maxdepth 1 -path '*[0-9][0-9]-[0-9][0-9]' -a -type 'd' -a -mtime +14 -print`
fi
if [ "${S3ENABLE:-false}" == "true" ]; then
    if [ "${EC2:-false}" == "true" ]; then
	export LOCAL_HOSTNAME=`curl http://169.254.169.254/latest/meta-data/local-hostname`
    else
	export LOCAL_HOSTNAME=`hostname --fqdn`
    fi
    s3cmd sync /usr/share/docassemble/backup/ s3://${S3BUCKET}/backup/${LOCAL_HOSTNAME}/
fi
if [ "${AZUREENABLE:-false}" == "true" ]; then
    if [ "${EC2:-false}" == "true" ]; then
	export LOCAL_HOSTNAME=`curl http://169.254.169.254/latest/meta-data/local-hostname`
    else
	export LOCAL_HOSTNAME=`hostname --fqdn`
    fi
    for the_file in $( find /usr/share/docassemble/backup/ -type f | cut -c 31- ); do
	blob-cmd -f cp "/usr/share/docassemble/backup/$the_file" 'blob://'${AZUREACCOUNTNAME}'/'${AZURECONTAINER}'/backup/'${LOCAL_HOSTNAME}'/'${the_file}
    done
    for the_dir in $( find /usr/share/docassemble/backup -maxdepth 1 -path '*[0-9][0-9]-[0-9][0-9]' -a -type 'd' -a -mtime +14 -print | cut -c 31- ); do
	blob-cmd -f rm 'blob://'${AZUREACCOUNTNAME}'/'${AZURECONTAINER}'/backup/'${LOCAL_HOSTNAME}'/'$( $the_dir )
	rm -rf /usr/share/docassemble/backup/$the_dir
    done
fi



