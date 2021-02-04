#! /bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DAPYTHONVERSION="${DAPYTHONVERSION:-3}"
export DA_DEFAULT_LOCAL="local3.8"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
source "${DA_ACTIVATE}"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
export CONTAINERROLE=":${CONTAINERROLE:-all}:"
source /dev/stdin < <(su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.base.read_config \"${DA_CONFIG_FILE}\"" www-data)
export LOGDIRECTORY="${LOGDIRECTORY:-${DA_ROOT}/log}"

set -- $LOCALE
export LANG=$1

function cmd_retry() {
    local -r cmd="$@"
    local -r -i max_attempts=4
    local -i attempt_num=1
    until $cmd
    do
        if ((attempt_num==max_attempts))
        then
            echo "Attempt $attempt_num failed.  Not trying again"
            return 1
        else
            if ((attempt_num==1)); then
                echo $cmd
            fi
            echo "Attempt $attempt_num failed."
            sleep $(((attempt_num++)**2))
        fi
    done
}

if [ "${S3ENABLE:-null}" == "null" ] && [ "${S3BUCKET:-null}" != "null" ]; then
    export S3ENABLE=true
fi

if [ "${S3ENABLE:-null}" == "true" ] && [ "${S3BUCKET:-null}" != "null" ] && [ "${S3ACCESSKEY:-null}" != "null" ] && [ "${S3SECRETACCESSKEY:-null}" != "null" ]; then
    export S3_ACCESS_KEY="${S3ACCESSKEY}"
    export S3_SECRET_KEY="${S3SECRETACCESSKEY}"
    export AWS_ACCESS_KEY_ID="$S3ACCESSKEY"
    export AWS_SECRET_ACCESS_KEY="$S3SECRETACCESSKEY"
fi

if [ "${S3ENDPOINTURL:-null}" != "null" ]; then
    export S4CMD_OPTS="--endpoint-url=\"${S3ENDPOINTURL}\""
fi

if [ "${AZUREENABLE:-null}" == "null" ] && [ "${AZUREACCOUNTNAME:-null}" != "null" ] && [ "${AZURECONTAINER:-null}" != "null" ]; then
    export AZUREENABLE=true
    cmd_retry blob-cmd add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
fi

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
    if [ "${USEHTTPS:-false}" == "true" ]; then
	if [ "${USELETSENCRYPT:-false}" == "true" ]; then
	    if [ -f /etc/letsencrypt/da_using_lets_encrypt ]; then
		export USE_PYTHON_3=1
		if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
		    supervisorctl --serverurl http://localhost:9001 stop apache2
		    certbot renew --apache --cert-name "${DAHOSTNAME}"
		    /etc/init.d/apache2 stop
		    supervisorctl --serverurl http://localhost:9001 start apache2
		fi
		if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
		    supervisorctl --serverurl http://localhost:9001 stop nginx
		    certbot renew --nginx --cert-name "${DAHOSTNAME}"
		    nginx -s stop &> /dev/null
		    supervisorctl --serverurl http://localhost:9001 start nginx
		fi
		if [ "${S3ENABLE:-false}" == "true" ]; then
		    cd /
		    if [ "${USELETSENCRYPT:-none}" != "none" ]; then
			rm -f /tmp/letsencrypt.tar.gz
			tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
			s4cmd -f put /tmp/letsencrypt.tar.gz "s3://${S3BUCKET}/letsencrypt.tar.gz"
		    fi
		    if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
			s4cmd dsync "/etc/apache2/sites-available" "s3://${S3BUCKET}/apache"
		    fi
		fi
		if [ "${AZUREENABLE:-false}" == "true" ]; then
		    cmd_retry blob-cmd add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
		    cd /
		    if [ "${USELETSENCRYPT:-none}" != "none" ]; then
			rm -f /tmp/letsencrypt.tar.gz
			tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
			cmd_retry blob-cmd -f cp /tmp/letsencrypt.tar.gz "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/letsencrypt.tar.gz"
		    fi
		    if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
			for the_file in $( find /etc/apache2/sites-available/ -type f ); do
			    target_file=`basename ${the_file}`
			    cmd_retry blob-cmd -f cp "${the_file}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/apache/${target_file}"
			done
		    fi
		fi
		if [ ! -f /etc/ssl/docassemble/exim.crt ] && [ ! -f /etc/ssl/docassemble/exim.key ]; then
		    cp "/etc/letsencrypt/live/${DAHOSTNAME}/fullchain.pem" /etc/exim4/exim.crt
		    cp "/etc/letsencrypt/live/${DAHOSTNAME}/privkey.pem" /etc/exim4/exim.key
		    chown root.Debian-exim /etc/exim4/exim.crt
		    chown root.Debian-exim /etc/exim4/exim.key
		    chmod 640 /etc/exim4/exim.crt
		    chmod 640 /etc/exim4/exim.key
		    supervisorctl --serverurl http://localhost:9001 stop exim4
		    supervisorctl --serverurl http://localhost:9001 start exim4
		fi
	    fi
	fi
    fi
fi

if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    "${DA_ROOT}/webapp/run-cron.sh" cron_daily
fi

if [ "${DABACKUPDAYS}" != "0" ]; then
    MONTHDAY=$(date +%m-%d)
    BACKUPDIR="${DA_ROOT}/backup/$MONTHDAY"
    rm -rf $BACKUPDIR
    mkdir -p $BACKUPDIR
    if [[ $CONTAINERROLE =~ .*:(all|web|celery|log|cron):.* ]]; then
	if [[ $CONTAINERROLE =~ .*:all:.* ]] && [ "${S3ENABLE:-false}" == "false" ] && [ "${AZUREENABLE:-false}" == "false" ]; then
	    rsync -auq "${DA_ROOT}/files" "${BACKUPDIR}/"
	fi
	rsync -auq "${DA_ROOT}/config" "${BACKUPDIR}/"
        if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
	    if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
	       rsync -auq /var/log/apache2/ "${LOGDIRECTORY}/" && chown -R www-data.www-data "${LOGDIRECTORY}"
	    fi
	    if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
	       rsync -auq /var/log/nginx/ "${LOGDIRECTORY}/" && chown -R www-data.www-data "${LOGDIRECTORY}"
	    fi
	fi
	rsync -auq "${LOGDIRECTORY}" "${BACKUPDIR}/"
    fi

    if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]]; then
        if [ -f /var/lib/redis/dump.rdb ]; then
	    cp /var/lib/redis/dump.rdb "${BACKUPDIR}/redis.rdb"
        fi
    elif [[ $CONTAINERROLE =~ .*:cron:.* ]] && [ "${REDIS:-redis://localhost}" != "redis://localhost" ]; then
	$REDISCLI --rdb "${BACKUPDIR}/redis.rdb"
    fi

    if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]]; then
	PGBACKUPDIR=`mktemp -d`
	chown postgres.postgres "${PGBACKUPDIR}"
	su postgres -c 'psql -Atc "SELECT datname FROM pg_database" postgres' | grep -v -e template -e postgres | awk -v backupdir="$PGBACKUPDIR" '{print "cd /tmp; su postgres -c \"pg_dump -F c -f " backupdir "/" $1 " " $1 "\""}' | bash
	rsync -auq "$PGBACKUPDIR/" "${BACKUPDIR}/postgres"
	if [ "${S3ENABLE:-false}" == "true" ]; then
	    s4cmd dsync "$PGBACKUPDIR" "s3://${S3BUCKET}/postgres"
	fi
	if [ "${AZUREENABLE:-false}" == "true" ]; then
	    for the_file in $( find "$PGBACKUPDIR/" -type f ); do
		target_file=`basename ${the_file}`
		cmd_retry blob-cmd -f cp "${the_file}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/postgres/${target_file}"
	    done
	fi
	rm -rf "${PGBACKUPDIR}"
    elif [[ $CONTAINERROLE =~ .*:cron:.* ]] && [ "${DBHOST:-localhost}" != "localhost" ] && [ "${DBBACKUP:-true}" == "true" ]; then
	PGBACKUPDIR=`mktemp -d`
	export PGPASSWORD="${DBPASSWORD:-abc123}"
	pg_dump -F c -f "${PGBACKUPDIR}/${DBNAME}" -h "${DBHOST}" -U "${DBUSER:-docassemble}" -w -p "${DBPORT:-5432}" "${DBNAME}"
	unset PGPASSWORD
	rsync -auq "$PGBACKUPDIR/" "${BACKUPDIR}/postgres"
	rm -rf "${PGBACKUPDIR}"
    fi
    if [ "${AZUREENABLE:-false}" == "false" ]; then
        rm -rf `find "${DA_ROOT}/backup" -maxdepth 1 -path '*[0-9][0-9]-[0-9][0-9]' -a -type 'd' -a -mtime +${DABACKUPDAYS:-14} -print`
    fi
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
    fi
    if [ "${AZUREENABLE:-false}" == "true" ]; then
	if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
	    BACKUPTARGET="blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/backup"
	else
	    if [ "${EC2:-false}" == "true" ]; then
		export LOCAL_HOSTNAME=`curl http://169.254.169.254/latest/meta-data/local-hostname`
	    else
		export LOCAL_HOSTNAME=`hostname --fqdn`
	    fi
	    BACKUPTARGET="blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/backup/${LOCAL_HOSTNAME}"
	fi
	for the_file in $( find "${DA_ROOT}/backup/" -type f | cut -c 31- ); do
	    cmd_retry blob-cmd -f cp "${DA_ROOT}/backup/${the_file}" "${BACKUPTARGET}/${the_file}"
	done
	for the_dir in $( find "${DA_ROOT}/backup" -maxdepth 1 -path '*[0-9][0-9]-[0-9][0-9]' -a -type 'd' -a -mtime +${DABACKUPDAYS:-14} -print | cut -c 31- ); do
	    for the_file in $( find "${DA_ROOT}/backup/${the_dir}" -type f | cut -c 31- ); do
		cmd_retry blob-cmd -f rm "${BACKUPTARGET}/${the_file}"
	    done
	    rm -rf "${DA_ROOT}/backup/$the_dir"
	done
    fi
fi
