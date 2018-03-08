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

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
    if [ "${USEHTTPS:-false}" == "true" ]; then
	if [ "${USELETSENCRYPT:-false}" == "true" ]; then
	    if [ -f /etc/letsencrypt/da_using_lets_encrypt ]; then
		/usr/bin/supervisorctl --serverurl http://localhost:9001 stop apache2
		cd /usr/share/docassemble/letsencrypt
		./letsencrypt-auto renew
		/etc/init.d/apache2 stop
		/usr/bin/supervisorctl --serverurl http://localhost:9001 start apache2
		if [ "${S3ENABLE:-false}" == "true" ]; then
		    cd /
		    if [ "${USELETSENCRYPT:-none}" != "none" ]; then
			rm -f /tmp/letsencrypt.tar.gz
			/bin/tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
			/usr/bin/s3cmd -q put /tmp/letsencrypt.tar.gz 's3://'${S3BUCKET}/letsencrypt.tar.gz
		    fi
		    /usr/bin/s3cmd -q sync /etc/apache2/sites-available/ 's3://'${S3BUCKET}/apache/
		fi
		if [ "${AZUREENABLE:-false}" == "true" ]; then
		    /usr/bin/blob-cmd add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
		    cd /
		    if [ "${USELETSENCRYPT:-none}" != "none" ]; then
			rm -f /tmp/letsencrypt.tar.gz
			/bin/tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
			/usr/bin/blob-cmd -f cp /tmp/letsencrypt.tar.gz 'blob://'${AZUREACCOUNTNAME}'/'${AZURECONTAINER}'/letsencrypt.tar.gz'
		    fi
		    for the_file in $( /usr/bin/find /etc/apache2/sites-available/ -type f ); do
			target_file=`basename $the_file`
			/usr/bin/blob-cmd -f cp "$the_file" 'blob://'${AZUREACCOUNTNAME}'/'${AZURECONTAINER}'/apache/'"$target_file"
		    done
		fi
		if [ ! -f /etc/ssl/docassemble/exim.crt ] && [ ! -f /etc/ssl/docassemble/exim.key ]; then
		    cp /etc/letsencrypt/live/${DAHOSTNAME}/fullchain.pem /etc/exim4/exim.crt
		    cp /etc/letsencrypt/live/${DAHOSTNAME}/privkey.pem /etc/exim4/exim.key
		    chown root.Debian-exim /etc/exim4/exim.crt
		    chown root.Debian-exim /etc/exim4/exim.key
		    chmod 640 /etc/exim4/exim.crt
		    chmod 640 /etc/exim4/exim.key
		    /usr/bin/supervisorctl --serverurl http://localhost:9001 stop exim4
		    /usr/bin/supervisorctl --serverurl http://localhost:9001 start exim4
		fi
	    fi
	fi
    fi
fi

MONTHDAY=$(date +%m-%d)
BACKUPDIR=/usr/share/docassemble/backup/$MONTHDAY
rm -rf $BACKUPDIR
mkdir -p $BACKUPDIR
if [[ $CONTAINERROLE =~ .*:(all|web|celery|log|cron):.* ]]; then
    /usr/bin/rsync -au /usr/share/docassemble/files $BACKUPDIR/
    /usr/bin/rsync -au /usr/share/docassemble/config $BACKUPDIR/
    /usr/bin/rsync -au --exclude '*/worker.log*' /usr/share/docassemble/log $BACKUPDIR/
fi

if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]]; then
    PGBACKUPDIR=`mktemp -d`
    chown postgres.postgres "$PGBACKUPDIR"
    su postgres -c '/usr/bin/psql -Atc "SELECT datname FROM pg_database" postgres' | grep -v -e template -e postgres | awk -v backupdir="$PGBACKUPDIR" '{print "cd /tmp; su postgres -c \"/usr/bin/pg_dump -F c -f " backupdir "/" $1 " " $1 "\""}' | bash
    /usr/bin/rsync -au "$PGBACKUPDIR/" $BACKUPDIR/postgres
    if [ "${S3ENABLE:-false}" == "true" ]; then
	/usr/bin/s3cmd sync "$PGBACKUPDIR/" s3://${S3BUCKET}/postgres/
    fi
    if [ "${AZUREENABLE:-false}" == "true" ]; then
	for the_file in $( find "$PGBACKUPDIR/" -type f ); do
	    target_file=`/usr/bin/basename $the_file`	    
	    /usr/bin/blob-cmd -f cp "$the_file" 'blob://'${AZUREACCOUNTNAME}'/'${AZURECONTAINER}"/postgres/$target_file"
	done
    fi
    rm -rf "$PGBACKUPDIR"
fi
if [ "${AZUREENABLE:-false}" == "false" ]; then
   rm -rf `/usr/bin/find /usr/share/docassemble/backup -maxdepth 1 -path '*[0-9][0-9]-[0-9][0-9]' -a -type 'd' -a -mtime +14 -print`
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
	for the_file in $( find "/usr/share/docassemble/backup/${the_dir}" -type f | cut -c 31- ); do
            blob-cmd -f rm 'blob://'${AZUREACCOUNTNAME}'/'${AZURECONTAINER}'/backup/'${LOCAL_HOSTNAME}'/'$( $the_file )
	done
	rm -rf /usr/share/docassemble/backup/$the_dir
    done
fi
