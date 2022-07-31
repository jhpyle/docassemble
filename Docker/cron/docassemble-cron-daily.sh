#! /bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DA_DEFAULT_LOCAL="local3.10"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
source "${DA_ACTIVATE}"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
export CONTAINERROLE=":${CONTAINERROLE:-all}:"
source /dev/stdin < <(su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.base.read_config \"${DA_CONFIG_FILE}\"" www-data)
export LOGDIRECTORY="${LOGDIRECTORY:-${DA_ROOT}/log}"

set -- $LOCALE
export LANG=$1

# Renew Let's Encrypt certificate; back up the certificates; copy certificates to exim
if [[ $CONTAINERROLE =~ .*:(all):.* ]] && [ "${USEHTTPS:-false}" == "true" ] && [ "${USELETSENCRYPT:-false}" == "true" ] && [ -f /etc/letsencrypt/da_using_lets_encrypt ]; then
    export USE_PYTHON_3=1
    if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
	certbot renew --apache --cert-name "${DAHOSTNAME}" --pre-hook "supervisorctl ${DASUPERVISOROPTS}--serverurl http://localhost:9001 stop apache2" --post-hook "/etc/init.d/apache2 stop; supervisorctl ${DASUPERVISOROPTS}--serverurl http://localhost:9001 start apache2"
    fi
    if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
	certbot renew --nginx --cert-name "${DAHOSTNAME}" --pre-hook "supervisorctl ${DASUPERVISOROPTS}--serverurl http://localhost:9001 stop nginx" --post-hook "nginx -s stop &> /dev/null; supervisorctl ${DASUPERVISOROPTS}--serverurl http://localhost:9001 start nginx"
    fi
    cd /
    rm -f /tmp/letsencrypt.tar.gz
    tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
    if [ "${S3ENABLE:-false}" == "true" ]; then
	s4cmd -f put /tmp/letsencrypt.tar.gz "s3://${S3BUCKET}/letsencrypt.tar.gz"
	if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
	    s4cmd dsync "/etc/apache2/sites-available" "s3://${S3BUCKET}/apache"
	fi
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	az storage blob upload --no-progress --overwrite true --only-show-errors --output none --container-name "${AZURECONTAINER}" -f /tmp/letsencrypt.tar.gz -n "letsencrypt.tar.gz"
	if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
	    for the_file in $( find /etc/apache2/sites-available/ -type f ); do
		target_file=`basename ${the_file}`
		az storage blob upload --no-progress --overwrite true --only-show-errors --output none --container-name "${AZURECONTAINER}" -f "${the_file}" -n "apache/${target_file}"
	    done
	fi
    else
	cp /tmp/letsencrypt.tar.gz "${DA_ROOT}/backup/letsencrypt.tar.gz"
    fi
    rm -f /tmp/letsencrypt.tar.gz
    if [ ! -f /etc/ssl/docassemble/exim.crt ] && [ ! -f /etc/ssl/docassemble/exim.key ]; then
	cp "/etc/letsencrypt/live/${DAHOSTNAME}/fullchain.pem" /etc/exim4/exim.crt
	cp "/etc/letsencrypt/live/${DAHOSTNAME}/privkey.pem" /etc/exim4/exim.key
	chown root.Debian-exim /etc/exim4/exim.crt
	chown root.Debian-exim /etc/exim4/exim.key
	chmod 640 /etc/exim4/exim.crt
	chmod 640 /etc/exim4/exim.key
	supervisorctl ${DASUPERVISOROPTS}--serverurl http://localhost:9001 stop exim4
	supervisorctl ${DASUPERVISOROPTS}--serverurl http://localhost:9001 start exim4
    fi
fi

# Run cron jobs in docassemble interviews
if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    "${DA_ROOT}/webapp/run-cron.sh" cron_daily
fi

# Backup log files. If not using cloud storage, also backup configuration and uploaded files.
if [ "${S3ENABLE:-false}" == "true" ]; then
    if [[ $CONTAINERROLE =~ .*:(all|log):.* ]]; then
        s4cmd dsync "${DA_ROOT}/log" "s3://${S3BUCKET}/log"
    fi
elif [ "${AZUREENABLE:-false}" == "true" ]; then
    if [[ $CONTAINERROLE =~ .*:(all|log):.* ]]; then
	let LOGDIRECTORYLENGTH=${#LOGDIRECTORY}+2
	for the_file in $(find "${LOGDIRECTORY}" -type f | cut -c ${LOGDIRECTORYLENGTH}-); do
	    az storage blob upload --no-progress --overwrite true --only-show-errors --output none --container-name "${AZURECONTAINER}" -f "${LOGDIRECTORY}/${the_file}" -n "log/${the_file}"
	done
    fi
elif [ "${DAREADONLYFILESYSTEM:-false}" == "false" ]; then
    if [[ $CONTAINERROLE =~ .*:(all|web|celery|log|cron):.* ]]; then
	rsync -auq --delete "${LOGDIRECTORY}" "${DA_ROOT}/backup/"
    fi
    if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
	rm -f "${DA_ROOT}/backup/config.yml"
	cp "${DA_CONFIG_FILE}" "${DA_ROOT}/backup/config.yml"
	rsync -auq --delete "${DA_ROOT}/files" "${DA_ROOT}/backup/"
    fi
fi

# if using a single server, back up web server logs so that they can be restored.
if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
    if [ "${S3ENABLE:-false}" == "true" ]; then
	if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
	    s4cmd dsync "/var/log/apache2" "s3://${S3BUCKET}/apachelogs"
	fi
	if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
	    s4cmd dsync "/var/log/nginx" "s3://${S3BUCKET}/nginxlogs"
	fi
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
	    for the_file in $(find /var/log/apache2 -type f | cut -c 18-); do
		az storage blob upload --no-progress --overwrite true --only-show-errors --output none --container-name "${AZURECONTAINER}" -f "/var/log/apache2/${the_file}" -n "apachelogs/${the_file}"
	    done
	fi
	if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
	    for the_file in $(find /var/log/nginx -type f | cut -c 16-); do
		az storage blob upload --no-progress --overwrite true --only-show-errors --output none --container-name "${AZURECONTAINER}" -f "/var/log/nginx/${the_file}" -n "nginxlogs/${the_file}"
	    done
	fi
    elif [ "${DAREADONLYFILESYSTEM:-false}" == "false" ]; then
	if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
	    mkdir -p "${DA_ROOT}/backup/apachelogs"
	    rsync -auq --delete /var/log/apache2/ "${DA_ROOT}/backup/apachelogs/"
	fi
	if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
	    mkdir -p "${DA_ROOT}/backup/nginxlogs"
	    rsync -auq /var/log/nginx/ "${DA_ROOT}/backup/nginxlogs/"
	fi
    fi
fi

# If this container is running a SQL server, back up PostgreSQL
if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]] && [ "$DBTYPE" == "postgresql" ]; then
    PGBACKUPDIR=`mktemp -d`
    chown postgres.postgres "${PGBACKUPDIR}"
    su postgres -c 'psql -Atc "SELECT datname FROM pg_database" postgres' | grep -v -e template -e postgres | awk -v backupdir="$PGBACKUPDIR" '{print "cd /tmp; su postgres -c \"pg_dump -F c -f " backupdir "/" $1 " " $1 "\""}' | bash
    if [ "${S3ENABLE:-false}" == "true" ]; then
	s4cmd dsync "$PGBACKUPDIR" "s3://${S3BUCKET}/postgres"
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	for the_file in $( find "$PGBACKUPDIR/" -type f ); do
	    target_file=`basename ${the_file}`
	    az storage blob upload --no-progress --overwrite true --only-show-errors --output none --container-name "${AZURECONTAINER}" -f "${the_file}" -n "postgres/${target_file}"
	done
    elif [ "${DAREADONLYFILESYSTEM:-false}" == "false" ]; then
	rsync -auq "$PGBACKUPDIR/" "${DA_ROOT}/backup/postgres"
    fi
fi

# If this container is running a Redis server, back up Redis
if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [ -f /var/lib/redis/dump.rdb ]; then
    if [ "${S3ENABLE:-false}" == "true" ]; then
	s4cmd -f put "/var/lib/redis/dump.rdb" "s3://${S3BUCKET}/redis.rdb"
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	az storage blob upload --no-progress --overwrite true --only-show-errors --output none --container-name "${AZURECONTAINER}" -f "/var/lib/redis/dump.rdb" -n "redis.rdb"
    elif [ "${DAREADONLYFILESYSTEM:-false}" == "false" ]; then
	cp /var/lib/redis/dump.rdb "${DA_ROOT}/backup/redis.rdb"
    fi
fi

# Create a rolling backup directory for today
if [ "${DAREADONLYFILESYSTEM:-false}" == "false" ] && [ "${DABACKUPDAYS}" != "0" ]; then
    MONTHDAY=$(date +%m-%d)
    BACKUPDIR="${DA_ROOT}/backup/$MONTHDAY"
    rm -rf $BACKUPDIR
    mkdir -p $BACKUPDIR

    # Copy Let's Encrypt certificates to rolling backup
    if [[ $CONTAINERROLE =~ .*:(all):.* ]] && [ "${USEHTTPS:-false}" == "true" ] && [ "${USELETSENCRYPT:-false}" == "true" ] && [ -f /etc/letsencrypt/da_using_lets_encrypt ]; then
	cd /
	rm -f /tmp/letsencrypt.tar.gz
	tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
	cp /tmp/letsencrypt.tar.gz "${BACKUPDIR}/"
	rm -f /tmp/letsencrypt.tar.gz
	cd /tmp
    fi

    # Copy uploaded files, configuration, and logs to the rolling backup
    if [[ $CONTAINERROLE =~ .*:(all|web|celery|log|cron):.* ]]; then
	if [ "${BACKUPFILESTORAGE:-true}" == "true" ] && [ "${S3ENABLE:-false}" == "false" ] && [ "${AZUREENABLE:-false}" == "false" ]; then
	    rsync -auq "${DA_ROOT}/files" "${BACKUPDIR}/"
	fi
	rsync -auq "${DA_ROOT}/config" "${BACKUPDIR}/"
	rsync -auq "${LOGDIRECTORY}" "${BACKUPDIR}/"
    fi

    # If this container is a redis server, copy the Redis database to the rolling backup
    if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]]; then
	if [ -f /var/lib/redis/dump.rdb ]; then
	    cp /var/lib/redis/dump.rdb "${BACKUPDIR}/redis.rdb"
	fi
    elif [[ $CONTAINERROLE =~ .*:cron:.* ]] && [ "${REDIS:-redis://localhost}" != "redis://localhost" ]; then
	$REDISCLI --rdb "${BACKUPDIR}/redis.rdb" &> /dev/null
    fi

    # If using PostgreSQL, copy the SQL database to the rolling backup
    if [ "$DBTYPE" == "postgresql" ]; then
	if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]]; then
	    rsync -auq "$PGBACKUPDIR/" "${BACKUPDIR}/postgres"
	elif [[ $CONTAINERROLE =~ .*:cron:.* ]] && [ "${DBHOST:-localhost}" != "localhost" ] && [ "${DBBACKUP:-true}" == "true" ]; then
	    PGBACKUPDIR=`mktemp -d`
	    export PGPASSWORD="${DBPASSWORD:-abc123}"
	    if [ "$DBPORT" != "" ]; then
		export PGPORT="${DBPORT}"
	    fi
	    if [ "$DBSSLMODE" != "" ]; then
		export PGSSLMODE="${DBSSLMODE}"
	    fi
	    if [ "$DBSSLCERT" != "" ]; then
		export PGSSLCERT="/etc/ssl/docassemble/${DBSSLCERT}"
	    fi
	    if [ "$DBSSLKEY" != "" ]; then
		export PGSSLKEY="/etc/ssl/docassemble/${DBSSLKEY}"
	    fi
	    if [ "$DBSSLROOTCERT" != "" ]; then
		export PGSSLROOTCERT="/etc/ssl/docassemble/${DBSSLROOTCERT}"
	    fi

	    pg_dump -F c -f "${PGBACKUPDIR}/${DBNAME}" -h "${DBHOST}" -U "${DBUSER:-docassemble}" -w -p "${DBPORT:-5432}" "${DBNAME}"
	    unset PGPASSWORD
	    unset PGSSLMODE
	    unset PGSSLCERT
	    unset PGSSLKEY
	    unset PGSSLROOTCERT
	    rsync -auq "$PGBACKUPDIR/" "${BACKUPDIR}/postgres"
	    rm -rf "${PGBACKUPDIR}"
	fi
    fi

    # Delete old rolling backup directories. If syncing to Azure, we do this below.
    if [ "${AZUREENABLE:-false}" == "false" ]; then
	rm -rf `find "${DA_ROOT}/backup" -maxdepth 1 -path '*[0-9][0-9]-[0-9][0-9]' -a -type 'd' -a -mtime +${DABACKUPDAYS:-14} -print`
    fi

    # If using cloud storage, copy the rolling backup to the cloud
    if [ "${S3ENABLE:-false}" == "true" ]; then
	if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
	    BACKUPTARGET="s3://${S3BUCKET}/backup"
	else
	    if [ "${EC2:-false}" == "true" ]; then
		export LOCAL_HOSTNAME=`curl http://169.254.169.254/latest/meta-data/local-hostname`
	    else
		export LOCAL_HOSTNAME=`hostname --fqdn`
	    fi
	    BACKUPTARGET="s3://${S3BUCKET}/backup/${LOCAL_HOSTNAME}"
	fi
	s4cmd --delete-removed dsync "${DA_ROOT}/backup" "${BACKUPTARGET}"
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
	    BACKUPTARGET="backup"
	else
	    if [ "${EC2:-false}" == "true" ]; then
		export LOCAL_HOSTNAME=`curl http://169.254.169.254/latest/meta-data/local-hostname`
	    else
		export LOCAL_HOSTNAME=`hostname --fqdn`
	    fi
	    BACKUPTARGET="backup/${LOCAL_HOSTNAME}"
	fi
	CURRENTBACKUP="${DA_ROOT}/backup"
	let CUTPOINT=${#CURRENTBACKUP}+2
	for the_file in $( find "${CURRENTBACKUP}/" -type f | cut -c ${CUTPOINT}- ); do
	    az storage blob upload --no-progress --overwrite true --only-show-errors --output none --container-name "${AZURECONTAINER}" -f "${CURRENTBACKUP}/${the_file}" -n "${BACKUPTARGET}/${the_file}"
	done
	for the_dir in $( find "${CURRENTBACKUP}" -maxdepth 1 -path '*[0-9][0-9]-[0-9][0-9]' -a -type 'd' -a -mtime +${DABACKUPDAYS:-14} -print | cut -c ${CUTPOINT}- ); do
	    for the_file in $( find "${CURRENTBACKUP}/${the_dir}" -type f | cut -c ${CUTPOINT}- ); do
		az storage blob delete --only-show-errors --output none --container-name "${AZURECONTAINER}" -n "${BACKUPTARGET}/${the_file}"
	    done
	    rm -rf "${CURRENTBACKUP}/$the_dir"
	done
    fi
fi

if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]]; then
    rm -rf "${PGBACKUPDIR}"
fi
