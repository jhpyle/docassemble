#! /bin/bash

export HOME=/root
export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DA_DEFAULT_LOCAL="local3.8"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"

echo "initialize: Activating Python with ${DA_ACTIVATE}" >&2

source "${DA_ACTIVATE}"

export DA_CONFIG_FILE_DIST="${DA_CONFIG_FILE_DIST:-${DA_ROOT}/config/config.yml.dist}"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
export CONTAINERROLE=":${CONTAINERROLE:-all}:"

function cmd_retry() {
    local -r cmd="$@"
    local -r -i max_attempts=4
    local -i attempt_num=1
    until $cmd
    do
        if ((attempt_num==max_attempts))
        then
            echo "initialize: Attempt $attempt_num failed.  Not trying again" >&2
            return 1
        else
            if ((attempt_num==1)); then
                echo $cmd
            fi
            echo "initialize: Attempt $attempt_num failed." >&2
            sleep $(((attempt_num++)**2))
        fi
    done
}

echo "initialize: config.yml is at" $DA_CONFIG_FILE >&2

echo "initialize: initialize starting" >&2

RESTOREFROMBACKUP=true

if [ -f /etc/da_running ]; then
    RESTOREFROMBACKUP=false
fi

touch /etc/da_running

export DEBIAN_FRONTEND=noninteractive
if [ "${DAALLOWUPDATES:-true}" == "true" ]; then
    apt-get clean &> /dev/null
    apt-get -q -y update &> /dev/null
fi

chsh -s /bin/bash www-data

echo "initialize: Determining if web browser already running" >&2

if [ -f /var/run/apache2/apache2.pid ]; then
    APACHE_PID=$(</var/run/apache2/apache2.pid)
    if kill -0 $APACHE_PID &> /dev/null; then
        APACHERUNNING=true
    else
        rm -f /var/run/apache2/apache2.pid
        APACHERUNNING=false
    fi
else
    APACHERUNNING=false
fi

if [ -f /var/run/nginx.pid ]; then
    NGINX_PID=$(</var/run/nginx.pid)
    if kill -0 $NGINX_PID &> /dev/null; then
        NGINXRUNNING=true
    else
        rm -f /var/run/nginx.pid
        NGINXRUNNING=false
    fi
else
    NGINXRUNNING=false
fi

echo "initialize: Determining if redis already running" >&2

if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && redis-cli ping &> /dev/null; then
    REDISRUNNING=true
else
    REDISRUNNING=false
fi

echo "initialize: Determining if cron already running" >&2

if [ -f /var/run/crond.pid ]; then
    CRON_PID=$(</var/run/crond.pid)
    if kill -0 $CRON_PID &> /dev/null; then
        CRONRUNNING=true
    else
        rm -f /var/run/crond.pid
        CRONRUNNING=false
    fi
else
    CRONRUNNING=false
fi

echo "initialize: Determining hostname" >&2

if [ "${USEHTTPS:-false}" == "false" ] && [ "${BEHINDHTTPSLOADBALANCER:-false}" == "false" ]; then
    URLROOT="http:\\/\\/"
else
    URLROOT="https:\\/\\/"
fi

if [ "${DAHOSTNAME:-none}" != "none" ]; then
    URLROOT="${URLROOT}${DAHOSTNAME}"
else
    if [ "${EC2:-false}" == "true" ]; then
        PUBLIC_HOSTNAME=`curl -s http://169.254.169.254/latest/meta-data/public-hostname`
    else
        PUBLIC_HOSTNAME=`hostname --fqdn`
    fi
    URLROOT="${URLROOT}${PUBLIC_HOSTNAME}"
fi

echo "initialize: Testing if S3 is in use" >&2

if [ "${S3ENABLE:-null}" == "null" ] && [ "${S3BUCKET:-null}" != "null" ]; then
    export S3ENABLE=true
fi

if [ "${S3ENABLE:-null}" == "true" ] && [ "${S3BUCKET:-null}" != "null" ] && [ "${S3ACCESSKEY:-null}" != "null" ] && [ "${S3SECRETACCESSKEY:-null}" != "null" ]; then
    export S3_ACCESS_KEY="$S3ACCESSKEY"
    export S3_SECRET_KEY="$S3SECRETACCESSKEY"
    export AWS_ACCESS_KEY_ID="$S3ACCESSKEY"
    export AWS_SECRET_ACCESS_KEY="$S3SECRETACCESSKEY"
    export AWS_DEFAULT_REGION="$S3REGION"
fi

if [ "${S3ENDPOINTURL:-null}" != "null" ]; then
    export S4CMD_OPTS="--endpoint-url=\"${S3ENDPOINTURL}\""
fi

if [ "${S3ENABLE:-null}" == "true" ]; then
    echo "initialize: Creating S3 bucket" >&2
    if [ "${USEMINIO:-false}" == "true" ]; then
        python -m docassemble.webapp.createminio "${S3ENDPOINTURL}" "${S3ACCESSKEY}" "${S3SECRETACCESSKEY}" "${S3BUCKET}"
    else
        s4cmd mb "s3://${S3BUCKET}" &> /dev/null
    fi
fi

echo "initialize: Testing if Azure Blob Storage is in use" >&2

if [ "${AZUREENABLE:-null}" == "null" ] && [ "${AZUREACCOUNTNAME:-null}" != "null" ] && [ "${AZUREACCOUNTKEY:-null}" != "null" ] && [ "${AZURECONTAINER:-null}" != "null" ]; then
    echo "initialize: Enabling Azure Blob Storage" >&2
    export AZUREENABLE=true
fi

echo "initialize: If S3 is in use, see if RabbitMQ is running in the cluster" >&2

if [ "${S3ENABLE:-false}" == "true" ] && [[ $CONTAINERROLE =~ .*:(web):.* ]] && [[ $(s4cmd ls s3://${S3BUCKET}/hostname-rabbitmq) ]] && [[ $(s4cmd ls s3://${S3BUCKET}/ip-rabbitmq) ]]; then
    TEMPKEYFILE=`mktemp`
    s4cmd -f get s3://${S3BUCKET}/hostname-rabbitmq $TEMPKEYFILE
    HOSTNAMERABBITMQ=$(<$TEMPKEYFILE)
    s4cmd -f get s3://${S3BUCKET}/ip-rabbitmq $TEMPKEYFILE
    IPRABBITMQ=$(<$TEMPKEYFILE)
    rm -f $TEMPKEYFILE
    if [ -n "$(grep $HOSTNAMERABBITMQ /etc/hosts)" ]; then
        sed -i "/$HOSTNAMERABBITMQ/d" /etc/hosts
    fi
    echo "$IPRABBITMQ $HOSTNAMERABBITMQ" >> /etc/hosts
fi

if [ "${AZUREENABLE:-false}" == "true" ]; then
    echo "initialize: Initializing azure" >&2
    cmd_retry blob-cmd -f -v add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
fi

echo "initialize: If Azure Blob Storage is in use, see if RabbitMQ is running in the cluster" >&2

if [ "${AZUREENABLE:-false}" == "true" ] && [[ $CONTAINERROLE =~ .*:(web):.* ]] && [[ $(python -m docassemble.webapp.list-cloud hostname-rabbitmq) ]] && [[ $(python -m docassemble.webapp.list-cloud ip-rabbitmq) ]]; then
    TEMPKEYFILE=`mktemp`
    echo "initialize: Copying hostname-rabbitmq" >&2
    cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/hostname-rabbitmq" "${TEMPKEYFILE}"
    HOSTNAMERABBITMQ=$(<$TEMPKEYFILE)
    echo "initialize: Copying ip-rabbitmq" >&2
    cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/ip-rabbitmq" "${TEMPKEYFILE}"
    IPRABBITMQ=$(<$TEMPKEYFILE)
    rm -f "${TEMPKEYFILE}"
    if [ -n "$(grep $HOSTNAMERABBITMQ /etc/hosts)" ]; then
        sed -i "/$HOSTNAMERABBITMQ/d" /etc/hosts
    fi
    echo "$IPRABBITMQ $HOSTNAMERABBITMQ" >> /etc/hosts
fi

echo "initialize: Determining public hostname" >&2

if [ "${EC2:-false}" == "true" ]; then
    export LOCAL_HOSTNAME=`curl -s http://169.254.169.254/latest/meta-data/local-hostname`
    export PUBLIC_HOSTNAME=`curl -s http://169.254.169.254/latest/meta-data/public-hostname`
else
    export LOCAL_HOSTNAME=`hostname --fqdn`
    export PUBLIC_HOSTNAME="${LOCAL_HOSTNAME}"
fi

if [ "${RESTOREFROMBACKUP}" == "true" ]; then
    echo "initialize: Restoring from backup" >&2
    if [ "${S3ENABLE:-false}" == "true" ]; then
	if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [[ $(s4cmd ls "s3://${S3BUCKET}/letsencrypt.tar.gz") ]]; then
	    echo "initialize: Restoring Let's Encrypt information from S3" >&2
            rm -f /tmp/letsencrypt.tar.gz
            s4cmd get "s3://${S3BUCKET}/letsencrypt.tar.gz" /tmp/letsencrypt.tar.gz
            cd /
            tar -xf /tmp/letsencrypt.tar.gz
            rm -f /tmp/letsencrypt.tar.gz
	else
            rm -f /etc/letsencrypt/da_using_lets_encrypt
	fi
	if [ "${DABACKUPDAYS}" != "0" ] && [[ $(s4cmd ls "s3://${S3BUCKET}/backup/${LOCAL_HOSTNAME}") ]]; then
	    echo "initialize: Restoring backup information from S3" >&2
	    s4cmd dsync "s3://${S3BUCKET}/backup/${LOCAL_HOSTNAME}" "${DA_ROOT}/backup"
	fi
	if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [[ $(s4cmd ls "s3://${S3BUCKET}/apache") ]]; then
	    echo "initialize: Restoring apache information from S3" >&2
	    s4cmd dsync "s3://${S3BUCKET}/apache" /etc/apache2/sites-available
	fi
	if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
	    if [[ $(s4cmd ls "s3://${S3BUCKET}/apachelogs") ]]; then
		echo "initialize: Restoring apache logs from S3" >&2
		s4cmd dsync "s3://${S3BUCKET}/apachelogs" /var/log/apache2
		chown root.adm /var/log/apache2/*
		chmod 640 /var/log/apache2/*
	    fi
	    if [[ $(s4cmd ls "s3://${S3BUCKET}/nginxlogs") ]]; then
		echo "initialize: Restoring NGINX logs from S3" >&2
		s4cmd dsync "s3://${S3BUCKET}/nginxlogs" /var/log/nginx
		chown www-data.adm /var/log/nginx/*
		chmod 640 /var/log/nginx/*
	    fi
	fi
	if [[ $CONTAINERROLE =~ .*:(all|log):.* ]] && [[ $(s4cmd ls "s3://${S3BUCKET}/log") ]]; then
	    echo "initialize: Restoring logs from S3" >&2
	    s4cmd dsync "s3://${S3BUCKET}/log" "${LOGDIRECTORY:-${DA_ROOT}/log}"
	    chown -R www-data.www-data "${LOGDIRECTORY:-${DA_ROOT}/log}"
	fi
	if [[ $(s4cmd ls "s3://${S3BUCKET}/config.yml") ]]; then
	    echo "initialize: Restoring configuration from S3" >&2
	    rm -f "$DA_CONFIG_FILE"
	    s4cmd get "s3://${S3BUCKET}/config.yml" "$DA_CONFIG_FILE"
	    chown www-data.www-data "$DA_CONFIG_FILE"
	fi
	if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [[ $(s4cmd ls "s3://${S3BUCKET}/redis.rdb") ]] && [ "$REDISRUNNING" = false ]; then
	    echo "initialize: Restoring Redis from S3" >&2
	    s4cmd -f get "s3://${S3BUCKET}/redis.rdb" "/var/lib/redis/dump.rdb"
	    chown redis.redis "/var/lib/redis/dump.rdb"
	fi
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [[ $(python -m docassemble.webapp.list-cloud letsencrypt.tar.gz) ]]; then
	    echo "initialize: Restoring Let's Encrypt information from Azure Blob Storage" >&2
	    rm -f /tmp/letsencrypt.tar.gz
	    echo "initialize: Copying let's encrypt" >&2
	    cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/letsencrypt.tar.gz" "/tmp/letsencrypt.tar.gz"
	    cd /
	    tar -xf /tmp/letsencrypt.tar.gz
	    rm -f /tmp/letsencrypt.tar.gz
	else
	    rm -f /etc/letsencrypt/da_using_lets_encrypt
	fi
	if [ "${DABACKUPDAYS}" != "0" ] && [[ $(python -m docassemble.webapp.list-cloud backup/${LOCAL_HOSTNAME}/) ]]; then
	    echo "initialize: Restoring backup information from Azure Blob Storage" >&2
	    BACKUPDIR="backup/${LOCAL_HOSTNAME}/"
	    let BACKUPDIRLENGTH=${#BACKUPDIR}+1
	    for the_file in $(python -m docassemble.webapp.list-cloud $BACKUPDIR | cut -c ${BACKUPDIRLENGTH}-); do
		echo "initialize: Found $the_file on Azure" >&2
		if ! [[ $the_file =~ /$ ]]; then
		    if [ ! -f "${DA_ROOT}/backup/${the_file}" ]; then
		       echo "initialize: Copying backup file" $the_file >&2
		       cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/backup/${LOCAL_HOSTNAME}/${the_file}" "${DA_ROOT}/backup/${the_file}"
		    fi
		fi
	    done
	fi
	if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [[ $(python -m docassemble.webapp.list-cloud apache/) ]]; then
	    echo "initialize: Restoring apache information from Azure Blob Storage" >&2
	    for the_file in $(python -m docassemble.webapp.list-cloud apache/ | cut -c 8-); do
		if ! [[ $the_file =~ /$ ]]; then
		    cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/apache/${the_file}" "/etc/apache2/sites-available/${the_file}"
		fi
	    done
	else
	    rm -f /etc/letsencrypt/da_using_lets_encrypt
	fi
	if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
	    if [[ $(python -m docassemble.webapp.list-cloud apachelogs/) ]]; then
		echo "initialize: Restoring apache logs from Azure Blob Storage" >&2
		for the_file in $(python -m docassemble.webapp.list-cloud apachelogs/ | cut -c 12-); do
		    if ! [[ $the_file =~ /$ ]]; then
			cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/apachelogs/${the_file}" "/var/log/apache2/${the_file}"
		    fi
		done
		chown root.adm /var/log/apache2/*
		chmod 640 /var/log/apache2/*
	    fi
	    if [[ $(python -m docassemble.webapp.list-cloud nginxlogs/) ]]; then
		echo "initialize: Restoring NGINX logs from Azure Blob Storage" >&2
		for the_file in $(python -m docassemble.webapp.list-cloud nginxlogs/ | cut -c 11-); do
		    if ! [[ $the_file =~ /$ ]]; then
			cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/nginxlogs/${the_file}" "/var/log/nginx/${the_file}"
		    fi
		done
		chown www-data.adm /var/log/nginx/*
		chmod 640 /var/log/nginx/*
	    fi
	fi
	if [[ $CONTAINERROLE =~ .*:(all|log):.* ]] && [[ $(python -m docassemble.webapp.list-cloud log) ]]; then
	    echo "initialize: Restoring logs from Azure Blob Storage" >&2
	    for the_file in $(python -m docassemble.webapp.list-cloud log/ | cut -c 5-); do
		if ! [[ $the_file =~ /$ ]]; then
		    cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/log/${the_file}" "${LOGDIRECTORY:-${DA_ROOT}/log}/${the_file}"
		fi
	    done
	    chown -R www-data.www-data "${LOGDIRECTORY:-${DA_ROOT}/log}"
	fi
	if [[ $(python -m docassemble.webapp.list-cloud config.yml) ]]; then
	    echo "initialize: Restoring configuration from Azure Blob Storage" >&2
	    rm -f "$DA_CONFIG_FILE"
	    echo "initialize: Copying config.yml" >&2
	    cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/config.yml" "${DA_CONFIG_FILE}"
	    chown www-data.www-data "${DA_CONFIG_FILE}"
	    ls -l "${DA_CONFIG_FILE}" >&2
	fi
	if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [[ $(python -m docassemble.webapp.list-cloud redis.rdb) ]] && [ "$REDISRUNNING" = false ]; then
	    echo "initialize: Restoring Redis from Azure Blob Storage" >&2
	    cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/redis.rdb" "/var/lib/redis/dump.rdb"
	    chown redis.redis "/var/lib/redis/dump.rdb"
	fi
    else
	if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [ -f "${DA_ROOT}/backup/letsencrypt.tar.gz" ]; then
	    echo "initialize: Restoring Let's Encrypt information from backup" >&2
	    cd /
	    tar -xf "${DA_ROOT}/backup/letsencrypt.tar.gz"
	fi
	if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [ -d "${DA_ROOT}/backup/apache" ]; then
	    echo "initialize: Restoring Apache information from backup" >&2
	    rsync -auq "${DA_ROOT}/backup/apache/" /etc/apache2/sites-available/
	fi
	if [[ $CONTAINERROLE =~ .*:(all):.* ]] && [ -d "${DA_ROOT}/backup/apachelogs" ]; then
	    echo "initialize: Restoring Apache logs from backup" >&2
	    rsync -auq "${DA_ROOT}/backup/apachelogs/" /var/log/apache2/
	    chown root.adm /var/log/apache2/*
	    chmod 640 /var/log/apache2/*
	fi
	if [[ $CONTAINERROLE =~ .*:(all):.* ]] && [ -d "${DA_ROOT}/backup/nginxlogs" ]; then
	    echo "initialize: Restoring NGINX logs from backup" >&2
	    rsync -auq "${DA_ROOT}/backup/nginxlogs/" /var/log/nginx/
	    chown www-data.adm /var/log/nginx/*
	    chmod 640 /var/log/nginx/*
	fi
	if [[ $CONTAINERROLE =~ .*:(all|log):.* ]] && [ -d "${DA_ROOT}/backup/log" ]; then
	    echo "initialize: Restoring logs from backup" >&2
	    rsync -auq "${DA_ROOT}/backup/log/" "${LOGDIRECTORY:-${DA_ROOT}/log}/"
	    chown -R www-data.www-data "${LOGDIRECTORY:-${DA_ROOT}/log}"
	fi
	if [ -f "${DA_ROOT}/backup/config.yml" ]; then
	    echo "initialize: Restoring Configuration from backup" >&2
	    cp "${DA_ROOT}/backup/config.yml" "${DA_CONFIG_FILE}"
	    chown www-data.www-data "${DA_CONFIG_FILE}"
	fi
	if [ -d "${DA_ROOT}/backup/files" ]; then
	    echo "initialize: Restoring files from backup" >&2
	    rsync -auq "${DA_ROOT}/backup/files" "${DA_ROOT}/"
	    chown -R www-data.www-data "${DA_ROOT}/files"
	fi
	if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [ -f "${DA_ROOT}/backup/redis.rdb" ] && [ "$REDISRUNNING" = false ]; then
	    echo "initialize: Restoring Redis from backup" >&2
	    cp "${DA_ROOT}/backup/redis.rdb" /var/lib/redis/dump.rdb
	    chown redis.redis "/var/lib/redis/dump.rdb"
	fi
    fi
fi

if [ "${BEHINDHTTPSLOADBALANCER:-null}" == "true" ] && [ "${XSENDFILE:-null}" == "null" ]; then
    export XSENDFILE=false
fi

if [ ! -f "$DA_CONFIG_FILE" ]; then
    DEFAULT_SECRET=$(python -m docassemble.base.generate_key)
    echo "initialize: There is no config file.  Creating one from source." >&2
    sed -e 's@{{DBPREFIX}}@'"${DBPREFIX:-postgresql+psycopg2:\/\/}"'@' \
        -e 's/{{DBNAME}}/'"${DBNAME:-docassemble}"'/' \
        -e 's/{{DBUSER}}/'"${DBUSER:-docassemble}"'/' \
        -e 's#{{DBPASSWORD}}#'"${DBPASSWORD:-abc123}"'#' \
        -e 's/{{DBHOST}}/'"${DBHOST:-null}"'/' \
        -e 's/{{DBPORT}}/'"${DBPORT:-null}"'/' \
        -e 's/{{DBTABLEPREFIX}}/'"${DBTABLEPREFIX:-null}"'/' \
        -e 's/{{DBBACKUP}}/'"${DBBACKUP:-true}"'/' \
        -e 's/{{DBSSLMODE}}/'"${DBSSLMODE:-null}"'/' \
        -e 's/{{DBSSLCERT}}/'"${DBSSLCERT:-null}"'/' \
        -e 's/{{DBSSLKEY}}/'"${DBSSLKEY:-null}"'/' \
        -e 's/{{DBSSLROOTCERT}}/'"${DBSSLROOTCERT:-null}"'/' \
        -e 's#{{CONFIGFROM}}#'"${CONFIGFROM:-null}"'#' \
        -e 's/{{S3ENABLE}}/'"${S3ENABLE:-false}"'/' \
        -e 's#{{S3ACCESSKEY}}#'"${S3ACCESSKEY:-null}"'#' \
        -e 's#{{S3SECRETACCESSKEY}}#'"${S3SECRETACCESSKEY:-null}"'#' \
        -e 's@{{S3ENDPOINTURL}}@'"${S3ENDPOINTURL:-null}"'@' \
        -e 's/{{S3BUCKET}}/'"${S3BUCKET:-null}"'/' \
        -e 's/{{S3REGION}}/'"${S3REGION:-null}"'/' \
        -e 's/{{AZUREENABLE}}/'"${AZUREENABLE:-false}"'/' \
        -e 's/{{AZUREACCOUNTNAME}}/'"${AZUREACCOUNTNAME:-null}"'/' \
        -e 's@{{AZUREACCOUNTKEY}}@'"${AZUREACCOUNTKEY:-null}"'@' \
        -e 's/{{AZURECONTAINER}}/'"${AZURECONTAINER:-null}"'/' \
        -e 's/{{DABACKUPDAYS}}/'"${DABACKUPDAYS:-14}"'/' \
        -e 's#{{REDIS}}#'"${REDIS:-null}"'#' \
        -e 's#{{RABBITMQ}}#'"${RABBITMQ:-null}"'#' \
        -e 's@{{DACELERYWORKERS}}@'"${DACELERYWORKERS:-null}"'@' \
        -e 's@{{TIMEZONE}}@'"${TIMEZONE:-null}"'@' \
        -e 's/{{EC2}}/'"${EC2:-false}"'/' \
        -e 's/{{COLLECTSTATISTICS}}/'"${COLLECTSTATISTICS:-false}"'/' \
        -e 's/{{KUBERNETES}}/'"${KUBERNETES:-false}"'/' \
        -e 's/{{USECLOUDURLS}}/'"${USECLOUDURLS:-false}"'/' \
        -e 's/{{USEMINIO}}/'"${USEMINIO:-false}"'/' \
        -e 's/{{USEHTTPS}}/'"${USEHTTPS:-false}"'/' \
        -e 's/{{USELETSENCRYPT}}/'"${USELETSENCRYPT:-false}"'/' \
        -e 's/{{LETSENCRYPTEMAIL}}/'"${LETSENCRYPTEMAIL:-null}"'/' \
        -e 's@{{LOGSERVER}}@'"${LOGSERVER:-null}"'@' \
        -e 's/{{DAHOSTNAME}}/'"${DAHOSTNAME:-none}"'/' \
        -e 's/{{LOCALE}}/'"${LOCALE:-null}"'/' \
        -e 's/{{SERVERADMIN}}/'"${SERVERADMIN:-webmaster@localhost}"'/' \
        -e 's@{{DASECRETKEY}}@'"${DEFAULT_SECRET}"'@' \
        -e 's@{{URLROOT}}@'"${URLROOT:-null}"'@' \
        -e 's@{{POSTURLROOT}}@'"${POSTURLROOT:-/}"'@' \
        -e 's/{{BEHINDHTTPSLOADBALANCER}}/'"${BEHINDHTTPSLOADBALANCER:-false}"'/' \
        -e 's/{{XSENDFILE}}/'"${XSENDFILE:-true}"'/' \
        -e 's/{{DAEXPOSEWEBSOCKETS}}/'"${DAEXPOSEWEBSOCKETS:-false}"'/' \
        -e 's/{{DAWEBSOCKETSIP}}/'"${DAWEBSOCKETSIP:-null}"'/' \
        -e 's/{{DAWEBSOCKETSPORT}}/'"${DAWEBSOCKETSPORT:-null}"'/' \
        -e 's/{{DAUPDATEONSTART}}/'"${DAUPDATEONSTART:-true}"'/' \
        -e 's/{{DAALLOWUPDATES}}/'"${DAALLOWUPDATES:-true}"'/' \
        -e 's/{{DAWEBSERVER}}/'"${DAWEBSERVER:-nginx}"'/' \
        -e 's/{{DASTABLEVERSION}}/'"${DASTABLEVERSION:-false}"'/' \
        -e 's/{{DASQLPING}}/'"${DASQLPING:-false}"'/' \
        -e 's/{{ENABLEUNOCONV}}/'"${ENABLEUNOCONV:-true}"'/' \
        -e 's/{{DAALLOWCONFIGURATIONEDITING}}/'"${DAALLOWCONFIGURATIONEDITING:-true}"'/' \
        -e 's/{{DAENABLEPLAYGROUND}}/'"${DAENABLEPLAYGROUND:-true}"'/' \
        -e 's/{{DADEBUG}}/'"${DADEBUG:-true}"'/g' \
        "$DA_CONFIG_FILE_DIST" > "$DA_CONFIG_FILE" || exit 1
fi
chown www-data.www-data "$DA_CONFIG_FILE"

echo "initialize: Defining environment variables from Configuration" >&2

source /dev/stdin < <(su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.base.read_config \"${DA_CONFIG_FILE}\"" www-data)
export LOGDIRECTORY="${LOGDIRECTORY:-${DA_ROOT}/log}"

echo "initialize: Running start hook" >&2

python -m docassemble.webapp.starthook "${DA_CONFIG_FILE}"

if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
    echo "initialize: Setting up NGINX basic configuration and uwsgi directory" >&2
    sed -e 's@{{DA_PYTHON}}@'"${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}"'@' \
        -e 's@{{DAWSGIROOT}}@'"${WSGIROOT}"'@' \
        -e 's@{{DA_ROOT}}@'"${DA_ROOT}"'@' \
        "${DA_ROOT}/config/docassemble.ini.dist" > "${DA_ROOT}/config/docassemble.ini"
    sed -e 's@{{DA_PYTHON}}@'"${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}"'@' \
        -e 's@{{DA_ROOT}}@'"${DA_ROOT}"'@' \
        "${DA_ROOT}/config/docassemblelog.ini.dist" > "${DA_ROOT}/config/docassemblelog.ini"
    mkdir -p /var/run/uwsgi
    chown www-data.www-data /var/run/uwsgi
fi

echo "initialize: If S3 is in use, save Configuration to S3" >&2

if [ "${S3ENABLE:-false}" == "true" ] && [[ ! $(s4cmd ls "s3://${S3BUCKET}/config.yml") ]]; then
    s4cmd -f put "${DA_CONFIG_FILE}" "s3://${S3BUCKET}/config.yml"
fi

echo "initialize: If S3 is in use, test if the files folder is missing" >&2

if [ "${S3ENABLE:-false}" == "true" ] && [[ ! $(s4cmd ls "s3://${S3BUCKET}/files") ]]; then
    echo "initialize: Test if a files folder is present locally" >&2
    if [ -d "${DA_ROOT}/files" ]; then
	echo "initialize: Copy files from local storage to S3" >&2
        for the_file in $(ls "${DA_ROOT}/files"); do
            if [[ $the_file =~ ^[0-9]+ ]]; then
                for sub_file in $(find "${DA_ROOT}/files/$the_file" -type f); do
                    file_number="${sub_file#${DA_ROOT}/files/}"
                    file_number="${file_number:0:15}"
                    file_directory="${DA_ROOT}/files/$file_number"
                    target_file="${sub_file#${file_directory}}"
                    file_number="${file_number//\//}"
                    file_number=$((16#$file_number))
                    s4cmd -f put "${sub_file}" "s3://${S3BUCKET}/files/${file_number}/${target_file}"
                done
            else
               s4cmd dsync "${DA_ROOT}/files/${the_file}" "s3://${S3BUCKET}/${the_file}"
            fi
        done
    fi
fi

if [ "${AZUREENABLE:-false}" == "true" ]; then
    echo "initialize: Initializing Azure Blob Storage if it is not already initialized" >&2
    cmd_retry blob-cmd -f -v add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
fi

echo "initialize: If Azure Blob Storage is in use, save Configuration to Azure Blob Storage" >&2

if [ "${AZUREENABLE:-false}" == "true" ] && [[ ! $(python -m docassemble.webapp.list-cloud config.yml) ]]; then
    cmd_retry blob-cmd -f cp "${DA_CONFIG_FILE}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/config.yml"
fi

echo "initialize: If Azure Blob Storage is in use, test if the files folder is missing" >&2

if [ "${AZUREENABLE:-false}" == "true" ] && [[ ! $(python -m docassemble.webapp.list-cloud files) ]]; then
    echo "initialize: Test if a files folder is present locally" >&2
    if [ -d "${DA_ROOT}/files" ]; then
	echo "initialize: Copy files from local storage to Azure Blob Storage" >&2
        for the_file in $(ls "${DA_ROOT}/files"); do
            if [[ $the_file =~ ^[0-9]+ ]]; then
                for sub_file in $(find "${DA_ROOT}/files/$the_file" -type f); do
                    file_number="${sub_file#${DA_ROOT}/files/}"
                    file_number="${file_number:0:15}"
                    file_directory="${DA_ROOT}/files/$file_number/"
                    target_file="${sub_file#${file_directory}}"
                    file_number="${file_number//\//}"
                    file_number=$((16#$file_number))
                    cmd_retry blob-cmd -f cp "${sub_file}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/files/${file_number}/${target_file}"
                done
            else
                for sub_file in $(find "${DA_ROOT}/files/$the_file" -type f); do
                    target_file="${sub_file#${DA_ROOT}/files/}"
                    cmd_retry blob-cmd -f cp "${sub_file}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/${target_file}"
                done
            fi
        done
    fi
fi

if [ "${DAHOSTNAME:-none}" == "none" ]; then
    export DAHOSTNAME="${PUBLIC_HOSTNAME}"
fi

if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]]; then
	echo "initialize: Setting up Apache" >&2
        a2dissite -q 000-default &> /dev/null
        a2dissite -q default-ssl &> /dev/null
        rm -f /etc/apache2/sites-available/000-default.conf
        rm -f /etc/apache2/sites-available/default-ssl.conf
        if [ "${DAHOSTNAME:-none}" != "none" ]; then
            if [ ! -f "/etc/letsencrypt/live/${DAHOSTNAME}/fullchain.pem" ]; then
                rm -f /etc/letsencrypt/da_using_lets_encrypt
            fi
            if [ ! -f /etc/apache2/sites-available/docassemble-ssl.conf ]; then
                cp "${DA_ROOT}/config/docassemble-ssl.conf.dist" /etc/apache2/sites-available/docassemble-ssl.conf
                rm -f /etc/letsencrypt/da_using_lets_encrypt
            fi
            if [ ! -f /etc/apache2/sites-available/docassemble-http.conf ]; then
                cp "${DA_ROOT}/config/docassemble-http.conf.dist" /etc/apache2/sites-available/docassemble-http.conf
                rm -f /etc/letsencrypt/da_using_lets_encrypt
            fi
            if [ ! -f /etc/apache2/sites-available/docassemble-log.conf ]; then
                cp "${DA_ROOT}/config/docassemble-log.conf.dist" /etc/apache2/sites-available/docassemble-log.conf
            fi
            if [ ! -f /etc/apache2/sites-available/docassemble-redirect.conf ]; then
                cp "${DA_ROOT}/config/docassemble-redirect.conf.dist" /etc/apache2/sites-available/docassemble-redirect.conf
            fi
        else
            if [ ! -f /etc/apache2/sites-available/docassemble-http.conf ]; then
                cp "${DA_ROOT}/config/docassemble-http.conf.dist" /etc/apache2/sites-available/docassemble-http.conf || exit 1
            fi
        fi
        a2ensite docassemble-http
    fi
fi

if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
    echo "initialize: Setting up NGINX configuration" >&2
    if [ "${USELETSENCRYPT:-false}" == "true" ] && [ -f "/etc/letsencrypt/live/${DAHOSTNAME}/fullchain.pem" ]; then
        DASSLCERTIFICATE="/etc/letsencrypt/live/${DAHOSTNAME}/fullchain.pem; # managed by Certbot"
        DASSLCERTIFICATEKEY="/etc/letsencrypt/live/${DAHOSTNAME}/privkey.pem; # managed by Certbot"
    else
        DASSLCERTIFICATE="/etc/ssl/docassemble/nginx.crt;"
        DASSLCERTIFICATEKEY="/etc/ssl/docassemble/nginx.key;"
    fi
    DASSLPROTOCOLS=${DASSLPROTOCOLS:-TLSv1.2}
    if [ ! -f "/etc/letsencrypt/live/${DAHOSTNAME}/fullchain.pem" ]; then
        rm -f /etc/letsencrypt/da_using_lets_encrypt
    fi

    if [ "${BEHINDHTTPSLOADBALANCER:-false}" == "true" ]; then
        DAREALIP="include ${DA_ROOT}/config/nginx-realip;"
        ln -sf /etc/nginx/sites-available/docassembleredirect /etc/nginx/sites-enabled/docassembleredirect
    else
        DAREALIP=""
        rm -f /etc/nginx/sites-enabled/docassembleredirect
    fi

    if [ "${POSTURLROOT}" == "/" ]; then
        DALOCATIONREWRITE=" "
    else
        DALOCATIONREWRITE="location = ${WSGIROOT} { rewrite ^ ${POSTURLROOT}; }"
    fi

    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]]; then
        rm -f /etc/nginx/sites-available/default
        rm -f /etc/nginx/sites-enabled/default
        if [ "${DAHOSTNAME:-none}" != "none" ]; then
            if [ ! -f /etc/nginx/sites-available/docassemblessl ]; then
                sed -e 's@{{DAHOSTNAME}}@'"${DAHOSTNAME:-localhost}"'@' \
                    -e 's@{{DALOCATIONREWRITE}}@'"${DALOCATIONREWRITE}"'@' \
                    -e 's@{{DAWSGIROOT}}@'"${WSGIROOT}"'@' \
                    -e 's@{{DAPOSTURLROOT}}@'"${POSTURLROOT}"'@' \
                    -e 's@{{DAREALIP}}@'"${DAREALIP}"'@' \
                    -e 's@{{DAMAXCONTENTLENGTH}}@'"${DAMAXCONTENTLENGTH}"'@' \
                    -e 's@{{DASSLCERTIFICATE}}@'"${DASSLCERTIFICATE}"'@' \
                    -e 's@{{DASSLCERTIFICATEKEY}}@'"${DASSLCERTIFICATEKEY}"'@' \
		    -e 's@{{DASSLPROTOCOLS}}@'"${DASSLPROTOCOLS}"'@' \
                    -e 's@{{DAWEBSOCKETSIP}}@'"${DAWEBSOCKETSIP:-127.0.0.1}"'@' \
                    -e 's@{{DAWEBSOCKETSPORT}}@'"${DAWEBSOCKETSPORT:-5000}"'@' \
                    -e 's@{{DALISTENPORT}}@'"${PORT:-80}"'@' \
                    "${DA_ROOT}/config/nginx-ssl.dist" > "/etc/nginx/sites-available/docassemblessl"
                rm -f /etc/letsencrypt/da_using_lets_encrypt
            fi
            if [ ! -f /etc/nginx/sites-available/docassemblehttp ]; then
                sed -e 's@{{DAHOSTNAME}}@'"${DAHOSTNAME:-localhost}"'@' \
                    -e 's@{{DALOCATIONREWRITE}}@'"${DALOCATIONREWRITE}"'@' \
                    -e 's@{{DAWSGIROOT}}@'"${WSGIROOT}"'@' \
                    -e 's@{{DAPOSTURLROOT}}@'"${POSTURLROOT}"'@' \
                    -e 's@{{DAREALIP}}@'"${DAREALIP}"'@' \
                    -e 's@{{DAMAXCONTENTLENGTH}}@'"${DAMAXCONTENTLENGTH}"'@' \
                    -e 's@{{DAWEBSOCKETSIP}}@'"${DAWEBSOCKETSIP:-127.0.0.1}"'@' \
                    -e 's@{{DAWEBSOCKETSPORT}}@'"${DAWEBSOCKETSPORT:-5000}"'@' \
                    -e 's@{{DALISTENPORT}}@'"${PORT:-80}"'@' \
                    "${DA_ROOT}/config/nginx-http.dist" > "/etc/nginx/sites-available/docassemblehttp"
                rm -f /etc/letsencrypt/da_using_lets_encrypt
            fi
            if [ ! -f /etc/nginx/sites-available/docassemblelog ]; then
                sed -e 's@{{DAHOSTNAME}}@'"${DAHOSTNAME:-localhost}"'@' \
                    -e 's@{{DAMAXCONTENTLENGTH}}@'"${DAMAXCONTENTLENGTH}"'@' \
                    "${DA_ROOT}/config/nginx-log.dist" > "/etc/nginx/sites-available/docassemblelog"
            fi
            if [ ! -f /etc/nginx/sites-available/docassembleredirect ]; then
                sed -e 's@{{DAHOSTNAME}}@'"${DAHOSTNAME:-localhost}"'@' \
                    "${DA_ROOT}/config/nginx-redirect.dist" > "/etc/nginx/sites-available/docassembleredirect"
            fi
            if [ ! -f /etc/nginx/sites-available/docassemblesslredirect ]; then
                sed -e 's@{{DAHOSTNAME}}@'"${DAHOSTNAME:-localhost}"'@' \
                    "${DA_ROOT}/config/nginx-ssl-redirect.dist" > "/etc/nginx/sites-available/docassemblesslredirect"
            fi
        else
            if [ ! -f /etc/nginx/sites-available/docassemblehttp ]; then
                sed -e 's@{{DAHOSTNAME}}@'"${DAHOSTNAME:-localhost}"'@' \
                    -e 's@{{DALOCATIONREWRITE}}@'"${DALOCATIONREWRITE}"'@' \
                    -e 's@{{DAWSGIROOT}}@'"${WSGIROOT}"'@' \
                    -e 's@{{DAPOSTURLROOT}}@'"${POSTURLROOT}"'@' \
                    -e 's@{{DAREALIP}}@'"${DAREALIP}"'@' \
                    -e 's@{{DAMAXCONTENTLENGTH}}@'"${DAMAXCONTENTLENGTH}"'@' \
                    -e 's@{{DAWEBSOCKETSIP}}@'"${DAWEBSOCKETSIP:-127.0.0.1}"'@' \
                    -e 's@{{DAWEBSOCKETSPORT}}@'"${DAWEBSOCKETSPORT:-5000}"'@' \
                    -e 's@{{DALISTENPORT}}@'"${PORT:-80}"'@' \
                    "${DA_ROOT}/config/nginx-http.dist" > "/etc/nginx/sites-available/docassemblehttp"
            fi
        fi
    fi
fi

echo "initialize: Setting and updating locale" >&2

if [ "${LOCALE:-undefined}" == "undefined" ]; then
    LOCALE="en_US.UTF-8 UTF-8"
fi

set -- $LOCALE
DA_LANGUAGE=$1
export LANG=$1

grep -q "^$LOCALE" /etc/locale.gen || { echo $LOCALE >> /etc/locale.gen && locale-gen ; }
update-locale LANG="${DA_LANGUAGE}"

if [ -n "$OTHERLOCALES" ]; then
    echo "initialize: Setting other locales" >&2
    NEWLOCALE=false
    for LOCALETOSET in "${OTHERLOCALES[@]}"; do
        grep -q "^$LOCALETOSET" /etc/locale.gen || { echo $LOCALETOSET >> /etc/locale.gen; NEWLOCALE=true; }
    done
    if [ "$NEWLOCALE" = true ]; then
        locale-gen
    fi
fi

if [ -n "$PACKAGES" ]; then
    echo "initialize: Installing Debian packages specified in the Configuration" >&2
    for PACKAGE in "${PACKAGES[@]}"; do
        apt-get -q -y install $PACKAGE &> /dev/null
    done
fi

if [ -n "$PYTHONPACKAGES" ]; then
    echo "initialize: Installing Python packages specified in the Configuration" >&2
    for PACKAGE in "${PYTHONPACKAGES[@]}"; do
        su -c "source \"${DA_ACTIVATE}\" && pip install $PACKAGE" www-data
    done
fi

if [ "${TIMEZONE:-undefined}" != "undefined" ] && [ -f /usr/share/zoneinfo/$TIMEZONE ]; then
    echo "initialize: Configuring time zone" >&2
    ln -fs /usr/share/zoneinfo/$TIMEZONE /etc/localtime
    dpkg-reconfigure -f noninteractive tzdata
fi

if [ "${S3ENABLE:-false}" == "true" ] || [ "${AZUREENABLE:-false}" == "true" ]; then
    echo "initialize: Registering this machine in the " >&2
    su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.webapp.cloud_register \"${DA_CONFIG_FILE}\"" www-data
fi

echo "initialize: Copying SSL certificates into position, if necessary" >&2

if [ ! -f "${DA_ROOT}/certs/apache.key" ] && [ -f "${DA_ROOT}/certs/apache.key.orig" ]; then
    mv "${DA_ROOT}/certs/apache.key.orig" "${DA_ROOT}/certs/apache.key"
fi
if [ ! -f "${DA_ROOT}/certs/apache.crt" ] && [ -f "${DA_ROOT}/certs/apache.crt.orig" ]; then
    mv "${DA_ROOT}/certs/apache.crt.orig" "${DA_ROOT}/certs/apache.crt"
fi
if [ ! -f "${DA_ROOT}/certs/apache.ca.pem" ] && [ -f "${DA_ROOT}/certs/apache.ca.pem.orig" ]; then
    mv "${DA_ROOT}/certs/apache.ca.pem.orig" "${DA_ROOT}/certs/apache.ca.pem"
fi
if [ ! -f "${DA_ROOT}/certs/nginx.key" ] && [ -f "${DA_ROOT}/certs/nginx.key.orig" ]; then
    mv "${DA_ROOT}/certs/nginx.key.orig" "${DA_ROOT}/certs/nginx.key"
fi
if [ ! -f "${DA_ROOT}/certs/nginx.crt" ] && [ -f "${DA_ROOT}/certs/nginx.crt.orig" ]; then
    mv "${DA_ROOT}/certs/nginx.crt.orig" "${DA_ROOT}/certs/nginx.crt"
fi
if [ ! -f "${DA_ROOT}/certs/nginx.ca.pem" ] && [ -f "${DA_ROOT}/certs/nginx.ca.pem.orig" ]; then
    mv "${DA_ROOT}/certs/nginx.ca.pem.orig" "${DA_ROOT}/certs/nginx.ca.pem"
fi
if [ ! -f "${DA_ROOT}/certs/exim.key" ] && [ -f "${DA_ROOT}/certs/exim.key.orig" ]; then
    mv "${DA_ROOT}/certs/exim.key.orig" "${DA_ROOT}/certs/exim.key"
fi
if [ ! -f "${DA_ROOT}/certs/exim.crt" ] && [ -f "${DA_ROOT}/certs/exim.crt.orig" ]; then
    mv "${DA_ROOT}/certs/exim.crt.orig" "${DA_ROOT}/certs/exim.crt"
fi
if [ ! -f "${DA_ROOT}/certs/postgresql.key" ] && [ -f "${DA_ROOT}/certs/postgresql.key.orig" ]; then
    mv "${DA_ROOT}/certs/postgresql.key.orig" "${DA_ROOT}/certs/postgresql.key"
fi
if [ ! -f "${DA_ROOT}/certs/postgresql.crt" ] && [ -f "${DA_ROOT}/certs/postgresql.crt.orig" ]; then
    mv "${DA_ROOT}/certs/postgresql.crt.orig" "${DA_ROOT}/certs/postgresql.crt"
fi
if [ ! -f "${DA_ROOT}/certs/apache.key" ] && [ -f "${DA_ROOT}/config/defaultcerts/apache.key.orig" ]; then
    cp "${DA_ROOT}/config/defaultcerts/apache.key.orig" "${DA_ROOT}/certs/apache.key"
fi
if [ ! -f "${DA_ROOT}/certs/apache.crt" ] && [ -f "${DA_ROOT}/config/defaultcerts/apache.crt.orig" ]; then
    cp "${DA_ROOT}/config/defaultcerts/apache.crt.orig" "${DA_ROOT}/certs/apache.crt"
fi
if [ ! -f "${DA_ROOT}/certs/apache.ca.pem" ] && [ -f "${DA_ROOT}/config/defaultcerts/apache.ca.pem.orig" ]; then
    cp "${DA_ROOT}/config/defaultcerts/apache.ca.pem.orig" "${DA_ROOT}/certs/apache.ca.pem"
fi
if [ ! -f "${DA_ROOT}/certs/nginx.key" ] && [ -f "${DA_ROOT}/config/defaultcerts/nginx.key.orig" ]; then
    cp "${DA_ROOT}/config/defaultcerts/nginx.key.orig" "${DA_ROOT}/certs/nginx.key"
fi
if [ ! -f "${DA_ROOT}/certs/nginx.crt" ] && [ -f "${DA_ROOT}/config/defaultcerts/nginx.crt.orig" ]; then
    cp "${DA_ROOT}/config/defaultcerts/nginx.crt.orig" "${DA_ROOT}/certs/nginx.crt"
fi
if [ ! -f "${DA_ROOT}/certs/nginx.ca.pem" ] && [ -f "${DA_ROOT}/config/defaultcerts/nginx.ca.pem.orig" ]; then
    cp "${DA_ROOT}/config/defaultcerts/nginx.ca.pem.orig" "${DA_ROOT}/certs/nginx.ca.pem"
fi
if [ ! -f "${DA_ROOT}/certs/exim.key" ] && [ -f "${DA_ROOT}/config/defaultcerts/exim.key.orig" ]; then
    cp "${DA_ROOT}/config/defaultcerts/exim.key.orig" "${DA_ROOT}/certs/exim.key"
fi
if [ ! -f "${DA_ROOT}/certs/exim.crt" ] && [ -f "${DA_ROOT}/config/defaultcerts/exim.crt.orig" ]; then
    cp "${DA_ROOT}/config/defaultcerts/exim.crt.orig" "${DA_ROOT}/certs/exim.crt"
fi
if [ ! -f "${DA_ROOT}/certs/postgresql.key" ] && [ -f "${DA_ROOT}/config/defaultcerts/postgresql.key.orig" ]; then
    cp "${DA_ROOT}/config/defaultcerts/postgresql.key.orig" "${DA_ROOT}/certs/postgresql.key"
fi
if [ ! -f "${DA_ROOT}/certs/postgresql.crt" ] && [ -f "${DA_ROOT}/config/defaultcerts/postgresql.crt.orig" ]; then
    cp "${DA_ROOT}/config/defaultcerts/postgresql.crt.orig" "${DA_ROOT}/certs/postgresql.crt"
fi

python -m docassemble.webapp.install_certs "${DA_CONFIG_FILE}" || exit 1

echo "initialize: Testing if PostgreSQL is running" >&2

if pg_isready -q; then
    PGRUNNING=true
else
    PGRUNNING=false
fi

if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]] && [ "$PGRUNNING" = false ] && [ "$DBTYPE" == "postgresql" ]; then
    echo "initialize: Starting PostgreSQL" >&2
    supervisorctl --serverurl http://localhost:9001 start postgres || exit 1
    sleep 4
    su -c "while ! pg_isready -q; do sleep 1; done" postgres
    echo "initialize: Testing if the database user exists" >&2
    roleexists=`su -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='${DBUSER:-docassemble}'\"" postgres`
    if [ -z "$roleexists" ]; then
	echo "initialize: Creating the database user" >&2
        echo "create role "${DBUSER:-docassemble}" with login password '"${DBPASSWORD:-abc123}"';" | su -c psql postgres || exit 1
    fi
    if [ "${RESTOREFROMBACKUP}" == "true" ]; then
	echo "initialize: Restoring SQL database" >&2
	if [ "${S3ENABLE:-false}" == "true" ] && [[ $(s4cmd ls s3://${S3BUCKET}/postgres) ]]; then
	    echo "initialize: Copying SQL file from S3" >&2
	    PGBACKUPDIR=`mktemp -d`
	    s4cmd dsync "s3://${S3BUCKET}/postgres" "$PGBACKUPDIR"
	elif [ "${AZUREENABLE:-false}" == "true" ] && [[ $(python -m docassemble.webapp.list-cloud postgres) ]]; then
	    echo "initialize: Copying SQL file from Azure Blob Storage" >&2
	    PGBACKUPDIR=`mktemp -d`
	    for the_file in $(python -m docassemble.webapp.list-cloud postgres/); do
		if ! [[ $the_file =~ /$ ]]; then
		    target_file=`basename "${the_file}"`
		    cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/${the_file}" "$PGBACKUPDIR/${target_file}"
		fi
	    done
	else
	    PGBACKUPDIR="${DA_ROOT}/backup/postgres"
	fi
	if [ -d "${PGBACKUPDIR}" ]; then
	    cd "$PGBACKUPDIR"
	    chown -R postgres.postgres "$PGBACKUPDIR"
	    for db in $( find . -maxdepth 1 -type f ! -iname ".*" ); do
		echo "initialize: Restoring postgres database $db" >&2
		pg_restore -f - -F c -C -c $db | su -c psql postgres
	    done
	    if [ "${S3ENABLE:-false}" == "true" ] || [ "${AZUREENABLE:-false}" == "true" ]; then
		cd /
		rm -rf $PGBACKUPDIR
	    fi
	    cd /tmp
	fi
    fi
    echo "initialize: Testing if database exists" >&2
    dbexists=`su -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='${DBNAME:-docassemble}'\"" postgres`
    if [ -z "$dbexists" ]; then
	echo "initialize: Creating SQL database" >&2
        echo "create database "${DBNAME:-docassemble}" owner "${DBUSER:-docassemble}" encoding UTF8;" | su -c psql postgres || exit 1
    fi
elif [ "$PGRUNNING" = false ] && [ "$DBTYPE" == "postgresql" ]; then
    export PGHOST="${DBHOST}"
    export PGUSER="${DBUSER}"
    export PGPASSWORD="${DBPASSWORD}"
    export PGDATABASE="postgres"
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
    echo "initialize: Testing if remote SQL server is ready" >&2
    while ! pg_isready -q; do sleep 1; done
    echo "initialize: Testing if remote SQL database exists" >&2
    dbexists=`psql -tAc "SELECT 1 FROM pg_database WHERE datname='${DBNAME:-docassemble}'"`
    if [ -z "$dbexists" ]; then
	echo "initialize: Creating remote SQL database" >&2
        echo "create database "${DBNAME:-docassemble}" owner "${DBUSER:-docassemble}";" | psql
    fi
    unset PGHOST
    unset PGUSER
    unset PGPASSWORD
    unset PGDATABASE
    unset PGPORT
    unset PGSSLMODE
    unset PGSSLCERT
    unset PGSSLKEY
    unset PGSSLROOTCERT
fi

if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    echo "initialize: Obtaining default e-mail and password from mounted credentials, if available" >&2
    if [ -f /configdata/initial_credentials ]; then
        echo "initialize: Found initial credentials" >&2
        source /configdata/initial_credentials
        rm -f /configdata/initial_credentials
    fi
    echo "initialize: Creating tables" >&2
    su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.webapp.create_tables \"${DA_CONFIG_FILE}\"" www-data
    unset DA_ADMIN_EMAIL
    unset DA_ADMIN_PASSWORD
    unset DA_ADMIN_API_KEY
fi

echo "initialize: Configuring log server, if applicable" >&2

if [ -f /etc/syslog-ng/syslog-ng.conf ] && [ ! -f "${DA_ROOT}/webapp/syslog-ng-orig.conf" ]; then
    cp /etc/syslog-ng/syslog-ng.conf "${DA_ROOT}/webapp/syslog-ng-orig.conf"
fi

OTHERLOGSERVER=false

if [[ $CONTAINERROLE =~ .*:(web|celery):.* ]]; then
    if [ "${LOGSERVER:-undefined}" != "undefined" ]; then
        OTHERLOGSERVER=true
    fi
fi

if [[ $CONTAINERROLE =~ .*:(log):.* ]] || [ "${LOGSERVER:-undefined}" == "null" ]; then
    OTHERLOGSERVER=false
fi

if [ "$OTHERLOGSERVER" = false ] && [ -f "${LOGDIRECTORY}/docassemble.log" ]; then
    chown www-data.www-data "${LOGDIRECTORY}/docassemble.log"
fi

if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [ "$REDISRUNNING" = false ]; then
    echo "initialize: Starting Redis" >&2
    supervisorctl --serverurl http://localhost:9001 start redis
fi

echo "initialize: Disabling pip version check" >&2

su -c "source \"${DA_ACTIVATE}\" && pip config set global.disable-pip-version-check true" www-data

echo "initialize: Checking to see if an alternative pip global index is used" >&2

if [ "${PIPINDEXURL:-null}" != "null" ]; then
    echo "initialize: Setting the alternative pip global index" >&2
    su -c "source \"${DA_ACTIVATE}\" && pip config set global.index-url ${PIPINDEXURL}" www-data
else
    echo "initialize: Using the standard pip global index" >&2
    su -c "source \"${DA_ACTIVATE}\" && pip config unset global.index-url" www-data &> /dev/null
fi

echo "initialize: Checking to see if extra pip index urls are used" >&2

if [ "${PIPEXTRAINDEXURLS:-null}" != "null" ]; then
    echo "initialize: Setting extra pip index urls" >&2
    su -c "source \"${DA_ACTIVATE}\" && pip config set global.extra-index-url ${PIPEXTRAINDEXURLS}" www-data
else
    echo "initialize: Not using extra pip index urls" >&2
    su -c "source \"${DA_ACTIVATE}\" && pip config unset global.extra-index-url" www-data &> /dev/null
fi

if [ "${DAUPDATEONSTART:-true}" == "true" ] && [ "${DAALLOWUPDATES:-true}" == "true" ]; then
    echo "initialize: Doing upgrading of packages" >&2
    su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.webapp.update \"${DA_CONFIG_FILE}\" initialize" www-data || exit 1
    touch "${DA_ROOT}/webapp/initialized"
fi

if [ "${DAUPDATEONSTART:-true}" == "initial" ] && [ ! -f "${DA_ROOT}/webapp/initialized" ] && [ "${DAALLOWUPDATES:-true}" == "true" ]; then
    echo "initialize: Doing initial upgrading of packages" >&2
    su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.webapp.update \"${DA_CONFIG_FILE}\" initialize" www-data || exit 1
    touch "${DA_ROOT}/webapp/initialized"
fi

echo "initialize: Testing if RabbitMQ is running" >&2

if rabbitmqctl status &> /dev/null; then
    RABBITMQRUNNING=true
else
    RABBITMQRUNNING=false
fi

if [[ $CONTAINERROLE =~ .*:(all|rabbitmq):.* ]] && [ "$RABBITMQRUNNING" = false ]; then
    echo "initialize: Starting RabbitMQ" >&2
    supervisorctl --serverurl http://localhost:9001 start rabbitmq
fi

if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]]; then
    echo "initialize: Checking if celery is already running" >&2
    if su -c "source \"${DA_ACTIVATE}\" && timeout 5s celery -A docassemble.webapp.worker status" www-data 2>&1 | grep -q `hostname`; then
        echo "initialize: Celery is running" >&2
        CELERYRUNNING=true;
    else
        echo "initialize: Celery is not already running" >&2
        CELERYRUNNING=false;
    fi
else
    CELERYRUNNING=false;
fi

if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]] && [ "$CELERYRUNNING" = false ]; then
    echo "initialize: Starting Celery" >&2
    supervisorctl --serverurl http://localhost:9001 start celery
    supervisorctl --serverurl http://localhost:9001 start celerysingle
fi

NASCENTRUNNING=true;
if [ "${USEHTTPS:-false}" == "true" ] && [ "${USELETSENCRYPT:-false}" == "true" ]; then
    echo "initialize: Stopping the nascent web server so that Let's Encrypt can run" >&2
    supervisorctl --serverurl http://localhost:9001 stop nascent &> /dev/null
    NASCENTRUNNING=false;
fi

if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
    function backup_nginx {
	echo "initialize: Backing up NGINX" >&2
        if [ "${S3ENABLE:-false}" == "true" ]; then
            if [ "${USELETSENCRYPT:-false}" == "true" ]; then
		echo "initialize: Copying Let's Encrypt to S3" >&2
                cd /
                rm -f /tmp/letsencrypt.tar.gz
                if [ -d etc/letsencrypt ]; then
                    tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
                    s4cmd -f put /tmp/letsencrypt.tar.gz "s3://${S3BUCKET}/letsencrypt.tar.gz"
                    rm -f /tmp/letsencrypt.tar.gz
                fi
            fi
        elif [ "${AZUREENABLE:-false}" == "true" ]; then
            if [ "${USELETSENCRYPT:-false}" == "true" ]; then
		echo "initialize: Copying Let's Encrypt to Azure Blob Storage" >&2
                cd /
                rm -f /tmp/letsencrypt.tar.gz
                if [ -d etc/letsencrypt ]; then
                    tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
                    cmd_retry blob-cmd -f cp /tmp/letsencrypt.tar.gz "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/letsencrypt.tar.gz"
                    rm -f /tmp/letsencrypt.tar.gz
                fi
            fi
        else
            if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
                if [ "${USELETSENCRYPT:-false}" == "true" ]; then
                    cd /
                    rm -f "${DA_ROOT}/backup/letsencrypt.tar.gz"
                    tar -zcf "${DA_ROOT}/backup/letsencrypt.tar.gz" etc/letsencrypt
                fi
            fi
        fi
    }

    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [ "$NGINXRUNNING" = false ]; then
	echo "initialize: Getting ready to start NGINX" >&2
        if [ "${WWWUID:-none}" != "none" ] && [ "${WWWGID:-none}" != "none" ] && [ `id -u www-data` != $WWWUID ]; then
	    echo "initialize: Changing the UID and GID of files" >&2
            OLDUID=`id -u www-data`
            OLDGID=`id -g www-data`

            usermod -o -u $WWWUID www-data
            groupmod -o -g $WWWGID www-data
            find / -user $OLDUID -exec chown -h www-data {} \;
            find / -group $OLDGID -exec chgrp -h www-data {} \;
            if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]] && [ "$CELERYRUNNING" = false ]; then
                supervisorctl --serverurl http://localhost:9001 stop celery
                supervisorctl --serverurl http://localhost:9001 stop celerysingle
            fi
            supervisorctl --serverurl http://localhost:9001 reread
            supervisorctl --serverurl http://localhost:9001 update
            if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]] && [ "$CELERYRUNNING" = false ]; then
                supervisorctl --serverurl http://localhost:9001 start celery
                supervisorctl --serverurl http://localhost:9001 start celerysingle
            fi
        fi
        if [ "${USEHTTPS:-false}" == "true" ]; then
	    echo "initialize: Configuring HTTPS" >&2
            rm -f /etc/nginx/sites-enabled/docassemblehttp
            ln -sf /etc/nginx/sites-available/docassemblessl /etc/nginx/sites-enabled/docassemblessl
            if [ "${USELETSENCRYPT:-false}" == "true" ]; then
		echo "initialize: Running Let's Encrypt" >&2
                export USE_PYTHON_3=1
                if [ -f /etc/letsencrypt/da_using_lets_encrypt ]; then
                    certbot renew --nginx --cert-name "${DAHOSTNAME}"
                else
                    certbot --nginx --quiet --email "${LETSENCRYPTEMAIL}" --agree-tos --no-redirect -d "${DAHOSTNAME}" && touch /etc/letsencrypt/da_using_lets_encrypt
                fi
                nginx -s stop &> /dev/null
                touch /etc/letsencrypt/da_using_lets_encrypt
            else
                rm -f /etc/letsencrypt/da_using_lets_encrypt
            fi
        else
	    echo "initialize: Not using HTTPS" >&2
            rm -f /etc/letsencrypt/da_using_lets_encrypt
            rm -f /etc/nginx/sites-enabled/docassemblessl
            ln -sf /etc/nginx/sites-available/docassemblehttp /etc/nginx/sites-enabled/docassemblehttp
        fi
    fi
    backup_nginx

    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
	echo "initialize: Starting websockets" >&2
        supervisorctl --serverurl http://localhost:9001 start websockets
    fi

    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
	echo "initialize: Starting uwsgi" >&2
        supervisorctl --serverurl http://localhost:9001 start uwsgi
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]]; then
        if [ "$NGINXRUNNING" = false ]; then
	    if [ "$NASCENTRUNNING" = true ]; then
		echo "initialize: Stopping the nascent web server" >&2
		supervisorctl --serverurl http://localhost:9001 stop nascent &> /dev/null
	    fi
	    echo "initialize: Starting NGINX" >&2
            supervisorctl --serverurl http://localhost:9001 start nginx
        fi
    fi
fi

if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
    echo "initialize: Getting ready to start Apache" >&2
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [ "$APACHERUNNING" = false ]; then
        rm -f /etc/apache2/ports.conf
    fi

    function backup_apache {
	echo "initialize: Backing up Apache" >&2
        if [ "${S3ENABLE:-false}" == "true" ]; then
            if [ "${USELETSENCRYPT:-false}" == "true" ]; then
		echo "initialize: Copying Let's Encrypt to S3" >&2
                cd /
                rm -f /tmp/letsencrypt.tar.gz
                if [ -d etc/letsencrypt ]; then
                    tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
                    s4cmd -f put /tmp/letsencrypt.tar.gz "s3://${S3BUCKET}/letsencrypt.tar.gz"
                    rm -f /tmp/letsencrypt.tar.gz
                fi
            fi
            if [[ $CONTAINERROLE =~ .*:(all):.* ]] || [[ ! $(python -m docassemble.webapp.list-cloud apache) ]]; then
		echo "initialize: Copying Apache to S3" >&2
                s4cmd dsync "/etc/apache2/sites-available" "s3://${S3BUCKET}/apache"
            fi
        elif [ "${AZUREENABLE:-false}" == "true" ]; then
            if [ "${USELETSENCRYPT:-false}" == "true" ]; then
		echo "initialize: Copying Let's Encrypt to Azure Blob Storage" >&2
                cd /
                rm -f /tmp/letsencrypt.tar.gz
                if [ -d etc/letsencrypt ]; then
                    tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
                    cmd_retry blob-cmd -f cp /tmp/letsencrypt.tar.gz "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/letsencrypt.tar.gz"
                    rm -f /tmp/letsencrypt.tar.gz
                fi
            fi
	    echo "initialize: Looking for Apache folder on Azure Blob Storage, if applicable" >&2
            if [[ $CONTAINERROLE =~ .*:(all):.* ]] || [[ ! $(python -m docassemble.webapp.list-cloud apache) ]]; then
		echo "initialize: Copying Apache to Azure Blob Storage" >&2
                for the_file in $(find /etc/apache2/sites-available/ -type f); do
                    target_file=`basename "${the_file}"`
                    echo "initialize: Saving apache" >&2
                    cmd_retry blob-cmd -f cp "${the_file}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/apache/${target_file}"
                done
            fi
        else
            if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
                if [ "${USELETSENCRYPT:-false}" == "true" ]; then
                    cd /
                    rm -f "${DA_ROOT}/backup/letsencrypt.tar.gz"
                    tar -zcf "${DA_ROOT}/backup/letsencrypt.tar.gz" etc/letsencrypt
                fi
                mkdir -p "${DA_ROOT}/backup/apache"
                rsync -auq --delete /etc/apache2/sites-available/ "${DA_ROOT}/backup/apache/"
            fi
        fi
    }

    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [ "$APACHERUNNING" = false ]; then
	echo "initialize: Configuring Apache" >&2
        echo "Listen ${PORT:-80}" > /etc/apache2/ports.conf
        if [ "${DAPYTHONMANUAL:-0}" == "0" ]; then
            WSGI_VERSION=`apt-cache policy libapache2-mod-wsgi-py3 | grep '^  Installed:' | awk '{print $2}'`
            if [ "${WSGI_VERSION}" != '4.6.5-1' ]; then
                apt-get -q -y install libapache2-mod-wsgi-py3 &> /dev/null
                ln -sf /usr/lib/apache2/modules/mod_wsgi.so-3.6 /usr/lib/apache2/modules/mod_wsgi.so
            fi
        fi

        if [ "${DAPYTHONMANUAL:-0}" == "0" ]; then
            a2enmod wsgi &> /dev/null
        else
            a2dismod wsgi &> /dev/null
        fi

        if [ "${WWWUID:-none}" != "none" ] && [ "${WWWGID:-none}" != "none" ] && [ `id -u www-data` != $WWWUID ]; then
	    echo "initialize: Changing the UID and GID of files" >&2
            OLDUID=`id -u www-data`
            OLDGID=`id -g www-data`

            usermod -o -u $WWWUID www-data
            groupmod -o -g $WWWGID www-data
            find / -user $OLDUID -exec chown -h www-data {} \;
            find / -group $OLDGID -exec chgrp -h www-data {} \;
            if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]] && [ "$CELERYRUNNING" = false ]; then
                supervisorctl --serverurl http://localhost:9001 stop celery
                supervisorctl --serverurl http://localhost:9001 stop celerysingle
            fi
            supervisorctl --serverurl http://localhost:9001 reread
            supervisorctl --serverurl http://localhost:9001 update
            if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]] && [ "$CELERYRUNNING" = false ]; then
                supervisorctl --serverurl http://localhost:9001 start celery
                supervisorctl --serverurl http://localhost:9001 start celerysingle
            fi
        fi

        if [ "${BEHINDHTTPSLOADBALANCER:-false}" == "true" ]; then
            a2enmod remoteip
            a2enconf docassemble-behindlb
        else
            a2dismod remoteip
            a2disconf docassemble-behindlb
        fi
        echo -e "# This file is automatically generated" > /etc/apache2/conf-available/docassemble.conf
        if [ "${DAPYTHONMANUAL:-0}" == "3" ]; then
            echo -e "LoadModule wsgi_module ${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/lib/python3.5/site-packages/mod_wsgi/server/mod_wsgi-py35.cpython-35m-x86_64-linux-gnu.so" >> /etc/apache2/conf-available/docassemble.conf
        fi
        echo -e "WSGIPythonHome ${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}" >> /etc/apache2/conf-available/docassemble.conf
        echo -e "Timeout ${DATIMEOUT:-60}\nDefine DAHOSTNAME ${DAHOSTNAME}\nDefine DAPOSTURLROOT ${POSTURLROOT}\nDefine DAWSGIROOT ${WSGIROOT}\nDefine DASERVERADMIN ${SERVERADMIN}\nDefine DAWEBSOCKETSIP ${DAWEBSOCKETSIP}\nDefine DAWEBSOCKETSPORT ${DAWEBSOCKETSPORT}\nDefine DACROSSSITEDOMAINVALUE *\nDefine DALISTENPORT ${PORT:-80}" >> /etc/apache2/conf-available/docassemble.conf
        if [ "${BEHINDHTTPSLOADBALANCER:-false}" == "true" ]; then
            echo "Listen 8081" >> /etc/apache2/ports.conf
            a2ensite docassemble-redirect
        fi
        if [ "${USEHTTPS:-false}" == "true" ]; then
	    echo "initialize: Configuring HTTPS" >&2
            echo "Listen 443" >> /etc/apache2/ports.conf
            a2enmod ssl
            a2ensite docassemble-ssl
            if [ "${USELETSENCRYPT:-false}" == "true" ]; then
		echo "initialize: Running Let's Encrypt" >&2
                export USE_PYTHON_3=1
                if [ -f /etc/letsencrypt/da_using_lets_encrypt ]; then
                    certbot renew --apache --cert-name "${DAHOSTNAME}"
                else
                    certbot --apache --quiet --email "${LETSENCRYPTEMAIL}" --agree-tos --redirect -d "${DAHOSTNAME}" && touch /etc/letsencrypt/da_using_lets_encrypt
                fi
                /etc/init.d/apache2 stop
                touch /etc/letsencrypt/da_using_lets_encrypt
            else
                rm -f /etc/letsencrypt/da_using_lets_encrypt
            fi
        else
	    echo "initialize: Not using HTTPS" >&2
            rm -f /etc/letsencrypt/da_using_lets_encrypt
            a2dismod ssl
            a2dissite -q docassemble-ssl &> /dev/null
        fi
        backup_apache
    fi

    if [[ $CONTAINERROLE =~ .*:(log):.* ]] && [ "$APACHERUNNING" = false ]; then
        echo "Listen 8080" >> /etc/apache2/ports.conf
        a2enmod cgid
        a2ensite docassemble-log
    fi

    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
	echo "initialize: Starting websockets" >&2
        supervisorctl --serverurl http://localhost:9001 start websockets
    fi

    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [ "$APACHERUNNING" = false ]; then
	if [ "$NASCENTRUNNING" = true ]; then
	    echo "initialize: Stopping the nascent web server" >&2
	    supervisorctl --serverurl http://localhost:9001 stop nascent &> /dev/null
	fi
	echo "initialize: Starting Apache" >&2
        supervisorctl --serverurl http://localhost:9001 start apache2
    fi
fi

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
    echo "initialize: Test localhost through HTTP" >&2
    if [ "${USEHTTPS:-false}" == "false" ]; then
        curl -s http://localhost/ > /dev/null
    else
        curl -s -k https://localhost/ > /dev/null
    fi
    if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
        if [ "$APACHERUNNING" = false ]; then
	    echo "initialize: Restarting Apache" >&2
            supervisorctl --serverurl http://localhost:9001 stop apache2
            supervisorctl --serverurl http://localhost:9001 start apache2
        fi
    fi
fi

echo "initialize: Checking to see if unoconv should be started" >&2

if [ "$ENABLEUNOCONV" == "true" ] && command -v unoconv &> /dev/null; then
    echo "initialize: Starting unoconv" >&2
    supervisorctl --serverurl http://localhost:9001 start unoconv
fi

echo "initialize: Registering this server" >&2

su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.webapp.register \"${DA_CONFIG_FILE}\"" www-data

if [ "$CRONRUNNING" = false ]; then
    echo "initialize: Starting cron" >&2
    if ! grep -q '^CONTAINERROLE' /etc/crontab; then
        bash -c "set | grep -e '^CONTAINERROLE=' -e '^DA_PYTHON=' -e '^DA_CONFIG=' -e '^DA_ROOT='; cat /etc/crontab" > /tmp/crontab && cat /tmp/crontab > /etc/crontab && rm -f /tmp/crontab
    fi
    supervisorctl --serverurl http://localhost:9001 start cron
fi


if [[ $CONTAINERROLE =~ .*:(all|mail):.* && ($DBTYPE = "postgresql" || $DBTYPE = "mysql") ]]; then
    echo "initialize: Starting exim4" >&2
    if [ "${DBTYPE}" = "postgresql" ]; then
        cp "${DA_ROOT}/config/exim4-router-postgresql" /etc/exim4/dbrouter
        if [ "${DBHOST:-null}" != "null" ]; then
            echo -n 'hide pgsql_servers = '${DBHOST} > /etc/exim4/dbinfo
        else
            echo -n 'hide pgsql_servers = localhost' > /etc/exim4/dbinfo
        fi
        if [ "${DBPORT:-null}" != "null" ]; then
            echo -n '::'${DBPORT} >> /etc/exim4/dbinfo
        fi
        echo '/'${DBNAME}'/'${DBUSER}'/'${DBPASSWORD} >> /etc/exim4/dbinfo
    fi
    if [ "$DBTYPE" = "mysql" ]; then
        cp "${DA_ROOT}/config/exim4-router-mysql" /etc/exim4/dbrouter
        if [ "${DBHOST:-null}" != "null" ]; then
            echo -n 'hide mysql_servers = '${DBHOST} > /etc/exim4/dbinfo
        else
            echo -n 'hide mysql_servers = localhost' > /etc/exim4/dbinfo
        fi
        if [ "${DBPORT:-null}" != "null" ]; then
            echo -n '::'${DBPORT} >> /etc/exim4/dbinfo
        fi
        echo '/'${DBNAME}'/'${DBUSER}'/'${DBPASSWORD} >> /etc/exim4/dbinfo
    fi
    if [ "${DBTYPE}" = "postgresql" ]; then
        echo 'DAQUERY = select short from '${DBTABLEPREFIX}"shortener where short='\${quote_pgsql:\$local_part}'" >> /etc/exim4/dbinfo
    fi
    if [ "${DBTYPE}" = "mysql" ]; then
        echo 'DAQUERY = select short from '${DBTABLEPREFIX}"shortener where short='\${quote_mysql:\$local_part}'" >> /etc/exim4/dbinfo
    fi
    if [ -f /etc/ssl/docassemble/exim.crt ] && [ -f /etc/ssl/docassemble/exim.key ]; then
        cp /etc/ssl/docassemble/exim.crt /etc/exim4/exim.crt
        cp /etc/ssl/docassemble/exim.key /etc/exim4/exim.key
        chown root.Debian-exim /etc/exim4/exim.crt
        chown root.Debian-exim /etc/exim4/exim.key
        chmod 640 /etc/exim4/exim.crt
        chmod 640 /etc/exim4/exim.key
        echo 'MAIN_TLS_ENABLE = yes' >> /etc/exim4/dbinfo
    elif [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [ "${USELETSENCRYPT:-false}" == "true" ] && [ -f "/etc/letsencrypt/live/${DAHOSTNAME}/cert.pem" ] && [ -f "/etc/letsencrypt/live/${DAHOSTNAME}/privkey.pem" ]; then
        cp "/etc/letsencrypt/live/${DAHOSTNAME}/fullchain.pem" /etc/exim4/exim.crt
        cp "/etc/letsencrypt/live/${DAHOSTNAME}/privkey.pem" /etc/exim4/exim.key
        chown root.Debian-exim /etc/exim4/exim.crt
        chown root.Debian-exim /etc/exim4/exim.key
        chmod 640 /etc/exim4/exim.crt
        chmod 640 /etc/exim4/exim.key
        echo 'MAIN_TLS_ENABLE = yes' >> /etc/exim4/dbinfo
    else
        echo 'MAIN_TLS_ENABLE = no' >> /etc/exim4/dbinfo
    fi
    chmod og-rwx /etc/exim4/dbinfo
    supervisorctl --serverurl http://localhost:9001 start exim4
fi

if [[ $CONTAINERROLE =~ .*:(log):.* ]] || [ "$OTHERLOGSERVER" = true ]; then
    if [ -d /etc/syslog-ng ]; then
	echo "initialize: Starting log server" >&2
        if [ "$OTHERLOGSERVER" = true ]; then
            cp "${DA_ROOT}/webapp/syslog-ng-docker.conf" /etc/syslog-ng/syslog-ng.conf
            cp "${DA_ROOT}/webapp/docassemble-syslog-ng.conf" /etc/syslog-ng/conf.d/docassemble.conf
            sleep 5s
        else
            rm -f /etc/syslog-ng/conf.d/docassemble.conf
            cp "${DA_ROOT}/webapp/syslog-ng.conf" /etc/syslog-ng/syslog-ng.conf
        fi
        supervisorctl --serverurl http://localhost:9001 start syslogng
    fi
fi

echo "initialize: creating crashpad folder" >&2

mkdir -p /tmp/Crashpad/attachments
mkdir -p /tmp/Crashpad/completed
mkdir -p /tmp/Crashpad/new
mkdir -p /tmp/Crashpad/pending
touch /tmp/Crashpad/settings.dat
chmod -R ogu+rwx /tmp/Crashpad

function deregister {
    rm -f "${DA_ROOT}/webapp/ready"
    su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.webapp.deregister \"${DA_CONFIG_FILE}\"" www-data
    if [ "${S3ENABLE:-false}" == "true" ] || [ "${AZUREENABLE:-false}" == "true" ]; then
        su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.webapp.cloud_deregister" www-data
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
        if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
            #backup_apache
            if [ "$OTHERLOGSERVER" = false ]; then
                rsync -auq /var/log/apache2/ "${LOGDIRECTORY}/" && chown -R www-data.www-data "${LOGDIRECTORY}"
            fi
        fi
        if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
            #backup_nginx
            if [ "$OTHERLOGSERVER" = false ]; then
                rsync -auq /var/log/nginx/ "${LOGDIRECTORY}/" && chown -R www-data.www-data "${LOGDIRECTORY}"
            fi
        fi
    fi
    if [ "${S3ENABLE:-false}" == "true" ]; then
	if [[ $CONTAINERROLE =~ .*:(all|log):.* ]]; then
            s4cmd dsync "${DA_ROOT}/log" "s3://${S3BUCKET}/log"
        fi
        if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
            if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
                s4cmd dsync "/var/log/apache2" "s3://${S3BUCKET}/apachelogs"
            fi
            if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
                s4cmd dsync "/var/log/nginx" "s3://${S3BUCKET}/nginxlogs"
            fi
        fi
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
        if [[ $CONTAINERROLE =~ .*:(all|log):.* ]]; then
            echo "initialize: Saving log files to Azure Blob Storage" >&2
            let LOGDIRECTORYLENGTH=${#LOGDIRECTORY}+2
            for the_file in $(find "${LOGDIRECTORY}" -type f | cut -c ${LOGDIRECTORYLENGTH}-); do
                echo "initialize: Saving log file $the_file" >&2
                cmd_retry blob-cmd -f cp "${LOGDIRECTORY}/${the_file}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/log/${the_file}"
            done
        fi
        if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
            echo "initialize: Saving Apache log files to Azure Blob Storage" >&2
            if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
                for the_file in $(find /var/log/apache2 -type f | cut -c 18-); do
                    cmd_retry blob-cmd -f cp "/var/log/apache2/${the_file}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/apachelogs/${the_file}"
                done
            fi
            if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
                echo "initialize: Saving NGINX log files to Azure Blob Storage" >&2
                for the_file in $(find /var/log/nginx -type f | cut -c 16-); do
                    cmd_retry blob-cmd -f cp "/var/log/nginx/${the_file}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/nginxlogs/${the_file}"
                done
            fi
        fi
    else
        if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
            echo "initialize: Saving Configuration" >&2
            rm -f "${DA_ROOT}/backup/config.yml"
            cp "${DA_CONFIG_FILE}" "${DA_ROOT}/backup/config.yml"
            echo "initialize: Saving files" >&2
            rsync -auq --delete "${DA_ROOT}/files" "${DA_ROOT}/backup/"
            echo "initialize: Done saving files" >&2
        fi
        if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
            if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
                echo "initialize: Saving Apache log files" >&2
                mkdir -p "${DA_ROOT}/backup/apachelogs"
                rsync -auq --delete /var/log/apache2/ "${DA_ROOT}/backup/apachelogs/"
            fi
            if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
                echo "initialize: Saving NGINX log files" >&2
                mkdir -p "${DA_ROOT}/backup/nginxlogs"
                rsync -auq --delete /var/log/nginx/ "${DA_ROOT}/backup/nginxlogs/"
            fi
        fi
        echo "initialize: Saving log files" >&2
        rsync -auq --delete "${LOGDIRECTORY}/" "${DA_ROOT}/backup/log/"
    fi
    rm -f /etc/da_running
    echo "initialize: finished shutting down initialize" >&2
    kill %1
    exit 0
}

trap deregister SIGINT SIGTERM

touch "${DA_ROOT}/webapp/ready"
echo "initialize: Finished initializing" >&2
sleep infinity &
wait %1
