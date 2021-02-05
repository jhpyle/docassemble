#! /bin/bash

export HOME=/root
export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DAPYTHONVERSION="${DAPYTHONVERSION:-3}"
export DA_DEFAULT_LOCAL="local3.8"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"

echo "Activating with ${DA_ACTIVATE}"

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

echo "config.yml is at" $DA_CONFIG_FILE >&2

echo "1" >&2

export DEBIAN_FRONTEND=noninteractive
if [ "${DAALLOWUPDATES:-true}" == "true" ]; then
    apt-get clean &> /dev/null
    apt-get -q -y update &> /dev/null
fi

echo "2" >&2

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

echo "3" >&2

if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && redis-cli ping &> /dev/null; then
    REDISRUNNING=true
else
    REDISRUNNING=false
fi

echo "4" >&2

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

echo "5" >&2

if [ "${USEHTTPS:-false}" == "false" ] && [ "${BEHINDHTTPSLOADBALANCER:-false}" == "false" ]; then
    URLROOT="http:\\/\\/"
else
    URLROOT="https:\\/\\/"
fi

echo "6" >&2

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

echo "7" >&2

if [ "${S3ENABLE:-null}" == "null" ] && [ "${S3BUCKET:-null}" != "null" ]; then
    export S3ENABLE=true
fi

echo "8" >&2

if [ "${S3ENABLE:-null}" == "true" ] && [ "${S3BUCKET:-null}" != "null" ] && [ "${S3ACCESSKEY:-null}" != "null" ] && [ "${S3SECRETACCESSKEY:-null}" != "null" ]; then
    export S3_ACCESS_KEY="$S3ACCESSKEY"
    export S3_SECRET_KEY="$S3SECRETACCESSKEY"
    export AWS_ACCESS_KEY_ID="$S3ACCESSKEY"
    export AWS_SECRET_ACCESS_KEY="$S3SECRETACCESSKEY"
fi

if [ "${S3ENDPOINTURL:-null}" != "null" ]; then
    export S4CMD_OPTS="--endpoint-url=\"${S3ENDPOINTURL}\""
fi

if [ "${S3ENABLE:-null}" == "true" ]; then
    if [ "${USEMINIO:-false}" == "true" ]; then
        python -m docassemble.webapp.createminio "${S3ENDPOINTURL}" "${S3ACCESSKEY}" "${S3SECRETACCESSKEY}" "${S3BUCKET}"
    else
        s4cmd mb "s3://${S3BUCKET}" &> /dev/null
    fi
fi

echo "9" >&2

if [ "${AZUREENABLE:-null}" == "null" ] && [ "${AZUREACCOUNTNAME:-null}" != "null" ] && [ "${AZUREACCOUNTKEY:-null}" != "null" ] && [ "${AZURECONTAINER:-null}" != "null" ]; then
    echo "Enable azure" >&2
    export AZUREENABLE=true
fi

echo "10" >&2

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

echo "11" >&2

if [ "${AZUREENABLE:-false}" == "true" ]; then
    echo "Initializing azure" >&2
    cmd_retry blob-cmd -f -v add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
fi

echo "12" >&2

if [ "${AZUREENABLE:-false}" == "true" ] && [[ $CONTAINERROLE =~ .*:(web):.* ]] && [[ $(python -m docassemble.webapp.list-cloud hostname-rabbitmq) ]] && [[ $(python -m docassemble.webapp.list-cloud ip-rabbitmq) ]]; then
    TEMPKEYFILE=`mktemp`
    echo "Copying hostname-rabbitmq" >&2
    cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/hostname-rabbitmq" "${TEMPKEYFILE}"
    HOSTNAMERABBITMQ=$(<$TEMPKEYFILE)
    echo "Copying ip-rabbitmq" >&2
    cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/ip-rabbitmq" "${TEMPKEYFILE}"
    IPRABBITMQ=$(<$TEMPKEYFILE)
    rm -f "${TEMPKEYFILE}"
    if [ -n "$(grep $HOSTNAMERABBITMQ /etc/hosts)" ]; then
        sed -i "/$HOSTNAMERABBITMQ/d" /etc/hosts
    fi
    echo "$IPRABBITMQ $HOSTNAMERABBITMQ" >> /etc/hosts
fi

echo "13" >&2

if [ "${S3ENABLE:-false}" == "true" ]; then
    if [ "${EC2:-false}" == "true" ]; then
        export LOCAL_HOSTNAME=`curl -s http://169.254.169.254/latest/meta-data/local-hostname`
    else
        export LOCAL_HOSTNAME=`hostname --fqdn`
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [[ $(s4cmd ls "s3://${S3BUCKET}/letsencrypt.tar.gz") ]]; then
        rm -f /tmp/letsencrypt.tar.gz
        s4cmd get "s3://${S3BUCKET}/letsencrypt.tar.gz" /tmp/letsencrypt.tar.gz
        cd /
        tar -xf /tmp/letsencrypt.tar.gz
        rm -f /tmp/letsencrypt.tar.gz
    else
        rm -f /etc/letsencrypt/da_using_lets_encrypt
    fi
    if [ "${DABACKUPDAYS}" != "0" ] && [[ $(s4cmd ls "s3://${S3BUCKET}/backup/${LOCAL_HOSTNAME}") ]]; then
        s4cmd dsync "s3://${S3BUCKET}/backup/${LOCAL_HOSTNAME}" "${DA_ROOT}/backup"
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [[ $(s4cmd ls "s3://${S3BUCKET}/apache") ]]; then
        s4cmd dsync "s3://${S3BUCKET}/apache" /etc/apache2/sites-available
    fi
    if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
        if [[ $(s4cmd ls "s3://${S3BUCKET}/apachelogs") ]]; then
            s4cmd dsync "s3://${S3BUCKET}/apachelogs" /var/log/apache2
            chown root.adm /var/log/apache2/*
            chmod 640 /var/log/apache2/*
        fi
        if [[ $(s4cmd ls "s3://${S3BUCKET}/nginxlogs") ]]; then
            s4cmd dsync "s3://${S3BUCKET}/nginxlogs" /var/log/nginx
            chown www-data.adm /var/log/nginx/*
            chmod 640 /var/log/nginx/*
        fi
    fi
    if [[ $CONTAINERROLE =~ .*:(all|log):.* ]] && [[ $(s4cmd ls "s3://${S3BUCKET}/log") ]]; then
        s4cmd dsync "s3://${S3BUCKET}/log" "${LOGDIRECTORY:-${DA_ROOT}/log}"
        chown -R www-data.www-data "${LOGDIRECTORY:-${DA_ROOT}/log}"
    fi
    if [[ $(s4cmd ls "s3://${S3BUCKET}/config.yml") ]]; then
        rm -f "$DA_CONFIG_FILE"
        s4cmd get "s3://${S3BUCKET}/config.yml" "$DA_CONFIG_FILE"
        chown www-data.www-data "$DA_CONFIG_FILE"
    fi
    if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [[ $(s4cmd ls "s3://${S3BUCKET}/redis.rdb") ]] && [ "$REDISRUNNING" = false ]; then
        s4cmd -f get "s3://${S3BUCKET}/redis.rdb" "/var/lib/redis/dump.rdb"
        chown redis.redis "/var/lib/redis/dump.rdb"
    fi
elif [ "${AZUREENABLE:-false}" == "true" ]; then
    if [ "${EC2:-false}" == "true" ]; then
        export LOCAL_HOSTNAME=`curl -s http://169.254.169.254/latest/meta-data/local-hostname`
    else
        export LOCAL_HOSTNAME=`hostname --fqdn`
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [[ $(python -m docassemble.webapp.list-cloud letsencrypt.tar.gz) ]]; then
        rm -f /tmp/letsencrypt.tar.gz
        echo "Copying let's encrypt" >&2
        cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/letsencrypt.tar.gz" "/tmp/letsencrypt.tar.gz"
        cd /
        tar -xf /tmp/letsencrypt.tar.gz
        rm -f /tmp/letsencrypt.tar.gz
    else
        rm -f /etc/letsencrypt/da_using_lets_encrypt
    fi
    if [ "${DABACKUPDAYS}" != "0" ] && [[ $(python -m docassemble.webapp.list-cloud backup/${LOCAL_HOSTNAME}/) ]]; then
        BACKUPDIR="backup/${LOCAL_HOSTNAME}/"
        let BACKUPDIRLENGTH=${#BACKUPDIR}+1
        for the_file in $(python -m docassemble.webapp.list-cloud $BACKUPDIR | cut -c ${BACKUPDIRLENGTH}-); do
            echo "Found $the_file on Azure" >&2
            if ! [[ $the_file =~ /$ ]]; then
                if [ ! -f "${DA_ROOT}/backup/${the_file}" ]; then
                   echo "Copying backup file" $the_file >&2
                   cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/backup/${LOCAL_HOSTNAME}/${the_file}" "${DA_ROOT}/backup/${the_file}"
                fi
            fi
        done
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [[ $(python -m docassemble.webapp.list-cloud apache/) ]]; then
        echo "There are apache files on Azure" >&2
        for the_file in $(python -m docassemble.webapp.list-cloud apache/ | cut -c 8-); do
            echo "Found $the_file on Azure" >&2
            if ! [[ $the_file =~ /$ ]]; then
                echo "Copying apache file" $the_file >&2
                cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/apache/${the_file}" "/etc/apache2/sites-available/${the_file}"
            fi
        done
    else
        rm -f /etc/letsencrypt/da_using_lets_encrypt
    fi
    if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
        if [[ $(python -m docassemble.webapp.list-cloud apachelogs/) ]]; then
            echo "There are apache log files on Azure" >&2
            for the_file in $(python -m docassemble.webapp.list-cloud apachelogs/ | cut -c 12-); do
                echo "Found $the_file on Azure" >&2
                if ! [[ $the_file =~ /$ ]]; then
                    echo "Copying log file $the_file" >&2
                    cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/apachelogs/${the_file}" "/var/log/apache2/${the_file}"
                fi
            done
            chown root.adm /var/log/apache2/*
            chmod 640 /var/log/apache2/*
        fi
        if [[ $(python -m docassemble.webapp.list-cloud nginxlogs/) ]]; then
            echo "There are nginx log files on Azure" >&2
            for the_file in $(python -m docassemble.webapp.list-cloud nginxlogs/ | cut -c 11-); do
                echo "Found $the_file on Azure" >&2
                if ! [[ $the_file =~ /$ ]]; then
                    echo "Copying log file $the_file" >&2
                    cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/nginxlogs/${the_file}" "/var/log/nginx/${the_file}"
                fi
            done
            chown www-data.adm /var/log/nginx/*
            chmod 640 /var/log/nginx/*
        fi
    fi
    if [[ $CONTAINERROLE =~ .*:(all|log):.* ]] && [[ $(python -m docassemble.webapp.list-cloud log) ]]; then
        echo "There are log files on Azure" >&2
        for the_file in $(python -m docassemble.webapp.list-cloud log/ | cut -c 5-); do
            echo "Found $the_file on Azure" >&2
            if ! [[ $the_file =~ /$ ]]; then
                echo "Copying log file $the_file" >&2
                cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/log/${the_file}" "${LOGDIRECTORY:-${DA_ROOT}/log}/${the_file}"
            fi
        done
        chown -R www-data.www-data "${LOGDIRECTORY:-${DA_ROOT}/log}"
    fi
    if [[ $(python -m docassemble.webapp.list-cloud config.yml) ]]; then
        rm -f "$DA_CONFIG_FILE"
        echo "Copying config.yml" >&2
        cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/config.yml" "${DA_CONFIG_FILE}"
        chown www-data.www-data "${DA_CONFIG_FILE}"
        ls -l "${DA_CONFIG_FILE}" >&2
    fi
    if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [[ $(python -m docassemble.webapp.list-cloud redis.rdb) ]] && [ "$REDISRUNNING" = false ]; then
        echo "Copying redis" >&2
        cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/redis.rdb" "/var/lib/redis/dump.rdb"
        chown redis.redis "/var/lib/redis/dump.rdb"
    fi
else
    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [ -f "${DA_ROOT}/backup/letsencrypt.tar.gz" ]; then
        cd /
        tar -xf "${DA_ROOT}/backup/letsencrypt.tar.gz"
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [ -d "${DA_ROOT}/backup/apache" ]; then
        rsync -auq "${DA_ROOT}/backup/apache/" /etc/apache2/sites-available/
    fi
    if [[ $CONTAINERROLE =~ .*:(all):.* ]] && [ -d "${DA_ROOT}/backup/apachelogs" ]; then
        rsync -auq "${DA_ROOT}/backup/apachelogs/" /var/log/apache2/
        chown root.adm /var/log/apache2/*
        chmod 640 /var/log/apache2/*
    fi
    if [[ $CONTAINERROLE =~ .*:(all):.* ]] && [ -d "${DA_ROOT}/backup/nginxlogs" ]; then
        rsync -auq "${DA_ROOT}/backup/nginxlogs/" /var/log/nginx/
        chown www-data.adm /var/log/nginx/*
        chmod 640 /var/log/nginx/*
    fi
    if [[ $CONTAINERROLE =~ .*:(all|log):.* ]] && [ -d "${DA_ROOT}/backup/log" ]; then
        rsync -auq "${DA_ROOT}/backup/log/" "${LOGDIRECTORY:-${DA_ROOT}/log}/"
        chown -R www-data.www-data "${LOGDIRECTORY:-${DA_ROOT}/log}"
    fi
    if [ -f "${DA_ROOT}/backup/config.yml" ]; then
        cp "${DA_ROOT}/backup/config.yml" "${DA_CONFIG_FILE}"
        chown www-data.www-data "${DA_CONFIG_FILE}"
    fi
    if [ -d "${DA_ROOT}/backup/files" ]; then
        rsync -auq "${DA_ROOT}/backup/files" "${DA_ROOT}/"
        chown -R www-data.www-data "${DA_ROOT}/files"
    fi
    if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [ -f "${DA_ROOT}/backup/redis.rdb" ] && [ "$REDISRUNNING" = false ]; then
        cp "${DA_ROOT}/backup/redis.rdb" /var/lib/redis/dump.rdb
        chown redis.redis "/var/lib/redis/dump.rdb"
    fi
fi

echo "14" >&2

DEFAULT_SECRET=$(python -m docassemble.base.generate_key)

echo "15" >&2

if [ "${BEHINDHTTPSLOADBALANCER:-null}" == "true" ] && [ "${XSENDFILE:-null}" == "null" ]; then
    export XSENDFILE=false
fi

if [ ! -f "$DA_CONFIG_FILE" ]; then
    echo "There is no config file.  Creating one from source." >&2
    sed -e 's@{{DBPREFIX}}@'"${DBPREFIX:-postgresql+psycopg2:\/\/}"'@' \
        -e 's/{{DBNAME}}/'"${DBNAME:-docassemble}"'/' \
        -e 's/{{DBUSER}}/'"${DBUSER:-docassemble}"'/' \
        -e 's#{{DBPASSWORD}}#'"${DBPASSWORD:-abc123}"'#' \
        -e 's/{{DBHOST}}/'"${DBHOST:-null}"'/' \
        -e 's/{{DBPORT}}/'"${DBPORT:-null}"'/' \
        -e 's/{{DBTABLEPREFIX}}/'"${DBTABLEPREFIX:-null}"'/' \
        -e 's/{{DBBACKUP}}/'"${DBBACKUP:-true}"'/' \
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
        -e 's@{{REDIS}}@'"${REDIS:-null}"'@' \
        -e 's#{{RABBITMQ}}#'"${RABBITMQ:-null}"'#' \
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
        "$DA_CONFIG_FILE_DIST" > "$DA_CONFIG_FILE" || exit 1
fi
chown www-data.www-data "$DA_CONFIG_FILE"

echo "16" >&2

source /dev/stdin < <(su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.base.read_config \"${DA_CONFIG_FILE}\"" www-data)
export LOGDIRECTORY="${LOGDIRECTORY:-${DA_ROOT}/log}"

echo "16.1" >&2

python -m docassemble.webapp.starthook "${DA_CONFIG_FILE}"

echo "16.5" >&2

if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
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

echo "17" >&2

if [ "${S3ENABLE:-false}" == "true" ] && [[ ! $(s4cmd ls "s3://${S3BUCKET}/config.yml") ]]; then
    s4cmd -f put "${DA_CONFIG_FILE}" "s3://${S3BUCKET}/config.yml"
fi

if [ "${S3ENABLE:-false}" == "true" ] && [[ ! $(s4cmd ls "s3://${S3BUCKET}/files") ]]; then
    if [ -d "${DA_ROOT}/files" ]; then
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
echo "18" >&2

if [ "${AZUREENABLE:-false}" == "true" ]; then
    echo "Initializing azure" >&2
    cmd_retry blob-cmd -f -v add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
fi

echo "19" >&2

if [ "${AZUREENABLE:-false}" == "true" ] && [[ ! $(python -m docassemble.webapp.list-cloud config.yml) ]]; then
    echo "Saving config" >&2
    cmd_retry blob-cmd -f cp "${DA_CONFIG_FILE}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/config.yml"
fi

echo "19.5" >&2

if [ "${AZUREENABLE:-false}" == "true" ] && [[ ! $(python -m docassemble.webapp.list-cloud files) ]]; then
    if [ -d "${DA_ROOT}/files" ]; then
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

echo "20" >&2

if [ "${EC2:-false}" == "true" ]; then
    export LOCAL_HOSTNAME=`curl -s http://169.254.169.254/latest/meta-data/local-hostname`
    export PUBLIC_HOSTNAME=`curl -s http://169.254.169.254/latest/meta-data/public-hostname`
else
    export LOCAL_HOSTNAME=`hostname --fqdn`
    export PUBLIC_HOSTNAME="${LOCAL_HOSTNAME}"
fi

echo "21" >&2

if [ "${DAHOSTNAME:-none}" == "none" ]; then
    export DAHOSTNAME="${PUBLIC_HOSTNAME}"
fi

echo "22" >&2

if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]]; then
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
                    "${DA_ROOT}/config/nginx-http.dist" > "/etc/nginx/sites-available/docassemblehttp"
            fi
        fi
    fi
fi

echo "23" >&2

if [ "${LOCALE:-undefined}" == "undefined" ]; then
    LOCALE="en_US.UTF-8 UTF-8"
fi

echo "24" >&2

set -- $LOCALE
DA_LANGUAGE=$1
export LANG=$1

grep -q "^$LOCALE" /etc/locale.gen || { echo $LOCALE >> /etc/locale.gen && locale-gen ; }
update-locale LANG="${DA_LANGUAGE}"

echo "25" >&2

if [ -n "$OTHERLOCALES" ]; then
    NEWLOCALE=false
    for LOCALETOSET in "${OTHERLOCALES[@]}"; do
        grep -q "^$LOCALETOSET" /etc/locale.gen || { echo $LOCALETOSET >> /etc/locale.gen; NEWLOCALE=true; }
    done
    if [ "$NEWLOCALE" = true ]; then
        locale-gen
    fi
fi

echo "26" >&2

if [ -n "$PACKAGES" ]; then
    for PACKAGE in "${PACKAGES[@]}"; do
        apt-get -q -y install $PACKAGE &> /dev/null
    done
fi

echo "26.5" >&2

if [ -n "$PYTHONPACKAGES" ]; then
    for PACKAGE in "${PYTHONPACKAGES[@]}"; do
        su -c "source \"${DA_ACTIVATE}\" && pip install $PACKAGE" www-data
    done
fi

echo "27" >&2

if [ "${TIMEZONE:-undefined}" != "undefined" ] && [ -f /usr/share/zoneinfo/$TIMEZONE ]; then
    ln -fs /usr/share/zoneinfo/$TIMEZONE /etc/localtime
    dpkg-reconfigure -f noninteractive tzdata
fi

echo "28" >&2

if [ "${S3ENABLE:-false}" == "true" ] || [ "${AZUREENABLE:-false}" == "true" ]; then
    su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.webapp.cloud_register \"${DA_CONFIG_FILE}\"" www-data
fi

echo "29" >&2

if pg_isready -q; then
    PGRUNNING=true
else
    PGRUNNING=false
fi

if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]] && [ "$PGRUNNING" = false ] && [ "$DBTYPE" == "postgresql" ]; then
    supervisorctl --serverurl http://localhost:9001 start postgres || exit 1
    sleep 4
    su -c "while ! pg_isready -q; do sleep 1; done" postgres
    roleexists=`su -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='${DBUSER:-docassemble}'\"" postgres`
    if [ -z "$roleexists" ]; then
        echo "create role "${DBUSER:-docassemble}" with login password '"${DBPASSWORD:-abc123}"';" | su -c psql postgres || exit 1
    fi
    if [ "${S3ENABLE:-false}" == "true" ] && [[ $(s4cmd ls s3://${S3BUCKET}/postgres) ]]; then
        PGBACKUPDIR=`mktemp -d`
        s4cmd dsync "s3://${S3BUCKET}/postgres" "$PGBACKUPDIR"
    elif [ "${AZUREENABLE:-false}" == "true" ] && [[ $(python -m docassemble.webapp.list-cloud postgres) ]]; then
        echo "There are postgres files on Azure" >&2
        PGBACKUPDIR=`mktemp -d`
        for the_file in $(python -m docassemble.webapp.list-cloud postgres/); do
            echo "Found $the_file on Azure" >&2
            if ! [[ $the_file =~ /$ ]]; then
                target_file=`basename "${the_file}"`
                echo "Copying $the_file to $target_file" >&2
                cmd_retry blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/${the_file}" "$PGBACKUPDIR/${target_file}"
            fi
        done
    else
        PGBACKUPDIR="${DA_ROOT}/backup/postgres"
    fi
    if [ -d "${PGBACKUPDIR}" ]; then
        echo "Postgres database backup directory is $PGBACKUPDIR" >&2
        cd "$PGBACKUPDIR"
        chown -R postgres.postgres "$PGBACKUPDIR"
        for db in $( ls ); do
            echo "Restoring postgres database $db" >&2
            pg_restore -F c -C -c $db | su -c psql postgres
        done
        if [ "${S3ENABLE:-false}" == "true" ] || [ "${AZUREENABLE:-false}" == "true" ]; then
            cd /
            rm -rf $PGBACKUPDIR
        fi
        cd /tmp
    fi
    dbexists=`su -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='${DBNAME:-docassemble}'\"" postgres`
    if [ -z "$dbexists" ]; then
        echo "create database "${DBNAME:-docassemble}" owner "${DBUSER:-docassemble}" encoding UTF8;" | su -c psql postgres || exit 1
    fi
elif [ "$PGRUNNING" = false ] && [ "$DBTYPE" == "postgresql" ]; then
    export PGHOST="${DBHOST}"
    export PGUSER="${DBUSER}"
    export PGPASSWORD="${DBPASSWORD}"
    export PGDATABASE="postgres"
    while ! pg_isready -q; do sleep 1; done
    dbexists=`psql -tAc "SELECT 1 FROM pg_database WHERE datname='${DBNAME:-docassemble}'"`
    if [ -z "$dbexists" ]; then
        echo "create database "${DBNAME:-docassemble}" owner "${DBUSER:-docassemble}";" | psql
    fi
    unset PGHOST
    unset PGUSER
    unset PGPASSWORD
    unset PGDATABASE
fi

echo "29.5" >&2

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

python -m docassemble.webapp.install_certs "${DA_CONFIG_FILE}" || exit 1

echo "30" >&2

if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    if [ -f /configdata/initial_credentials ]; then
        echo "Found initial credentials" >&2
        source /configdata/initial_credentials
        rm -f /configdata/initial_credentials
    fi
    su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.webapp.create_tables \"${DA_CONFIG_FILE}\"" www-data
    unset DA_ADMIN_EMAIL
    unset DA_ADMIN_PASSWORD
fi

echo "31" >&2

if [ -f /etc/syslog-ng/syslog-ng.conf ] && [ ! -f "${DA_ROOT}/webapp/syslog-ng-orig.conf" ]; then
    cp /etc/syslog-ng/syslog-ng.conf "${DA_ROOT}/webapp/syslog-ng-orig.conf"
fi

echo "32" >&2

OTHERLOGSERVER=false

if [[ $CONTAINERROLE =~ .*:(web|celery):.* ]]; then
    if [ "${LOGSERVER:-undefined}" != "undefined" ]; then
        OTHERLOGSERVER=true
    fi
fi

echo "33" >&2

if [[ $CONTAINERROLE =~ .*:(log):.* ]] || [ "${LOGSERVER:-undefined}" == "null" ]; then
    OTHERLOGSERVER=false
fi

echo "34" >&2

if [ "$OTHERLOGSERVER" = false ] && [ -f "${LOGDIRECTORY}/docassemble.log" ]; then
    chown www-data.www-data "${LOGDIRECTORY}/docassemble.log"
fi

echo "36" >&2

if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [ "$REDISRUNNING" = false ]; then
    supervisorctl --serverurl http://localhost:9001 start redis
fi

echo "37" >&2

if [ "${DAUPDATEONSTART:-true}" = "true" ] && [ "${DAALLOWUPDATES:-true}" == "true" ]; then
    echo "Doing upgrading of packages" >&2
    su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.webapp.update \"${DA_CONFIG_FILE}\" initialize" www-data || exit 1
    touch "${DA_ROOT}/webapp/initialized"
fi

if [ "${DAUPDATEONSTART:-true}" = "initial" ] && [ ! -f "${DA_ROOT}/webapp/initialized" ] && [ "${DAALLOWUPDATES:-true}" == "true" ]; then
    echo "Doing initial upgrading of packages" >&2
    su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.webapp.update \"${DA_CONFIG_FILE}\" initialize" www-data || exit 1
    touch "${DA_ROOT}/webapp/initialized"
fi

echo "38" >&2

if rabbitmqctl status &> /dev/null; then
    RABBITMQRUNNING=true
else
    RABBITMQRUNNING=false
fi

if [[ $CONTAINERROLE =~ .*:(all|rabbitmq):.* ]] && [ "$RABBITMQRUNNING" = false ]; then
    supervisorctl --serverurl http://localhost:9001 start rabbitmq
fi

echo "39" >&2

if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]]; then
    echo "checking if celery is already running..." >&2
    if su -c "source \"${DA_ACTIVATE}\" && timeout 5s celery -A docassemble.webapp.worker status" www-data 2>&1 | grep -q `hostname`; then
        echo "celery is running" >&2
        CELERYRUNNING=true;
    else
        echo "celery is not already running" >&2
        CELERYRUNNING=false;
    fi
else
    CELERYRUNNING=false;
fi

echo "40" >&2

if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]] && [ "$CELERYRUNNING" = false ]; then
    supervisorctl --serverurl http://localhost:9001 start celery
fi

if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
    function backup_nginx {
        if [ "${S3ENABLE:-false}" == "true" ]; then
            if [ "${USELETSENCRYPT:-false}" == "true" ]; then
                cd /
                rm -f /tmp/letsencrypt.tar.gz
                if [ -d etc/letsencrypt ]; then
                    tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
                    s4cmd -f put /tmp/letsencrypt.tar.gz "s3://${S3BUCKET}/letsencrypt.tar.gz"
                    rm -f /tmp/letsencrypt.tar.gz
                fi
            fi
            #if [[ $CONTAINERROLE =~ .*:(all):.* ]] || [[ ! $(python -m docassemble.webapp.list-cloud nginx) ]]; then
            #    s4cmd dsync "/etc/nginx/sites-available" "s3://${S3BUCKET}/nginx"
            #fi
        elif [ "${AZUREENABLE:-false}" == "true" ]; then
            if [ "${USELETSENCRYPT:-false}" == "true" ]; then
                cd /
                rm -f /tmp/letsencrypt.tar.gz
                if [ -d etc/letsencrypt ]; then
                    tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
                    echo "Saving lets encrypt" >&2
                    cmd_retry blob-cmd -f cp /tmp/letsencrypt.tar.gz "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/letsencrypt.tar.gz"
                    rm -f /tmp/letsencrypt.tar.gz
                fi
            fi
            #if [[ $CONTAINERROLE =~ .*:(all):.* ]] || [[ ! $(python -m docassemble.webapp.list-cloud nginx) ]]; then
            #    for the_file in $(find /etc/nginx/sites-available/ -type f); do
            #        target_file=`basename "${the_file}"`
            #        echo "Saving nginx" >&2
            #        cmd_retry blob-cmd -f cp "${the_file}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/nginx/${target_file}"
            #    done
            #fi
        else
            if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
                if [ "${USELETSENCRYPT:-false}" == "true" ]; then
                    cd /
                    rm -f "${DA_ROOT}/backup/letsencrypt.tar.gz"
                    tar -zcf "${DA_ROOT}/backup/letsencrypt.tar.gz" etc/letsencrypt
                fi
                #rm -rf "${DA_ROOT}/backup/nginx"
                #mkdir -p "${DA_ROOT}/backup/nginx"
                #rsync -auq /etc/nginx/sites-available/ "${DA_ROOT}/backup/nginx/"
            fi
        fi
    }

    echo "41.2" >&2
    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [ "$NGINXRUNNING" = false ]; then
        if [ "${WWWUID:-none}" != "none" ] && [ "${WWWGID:-none}" != "none" ] && [ `id -u www-data` != $WWWUID ]; then
            OLDUID=`id -u www-data`
            OLDGID=`id -g www-data`

            usermod -o -u $WWWUID www-data
            groupmod -o -g $WWWGID www-data
            find / -user $OLDUID -exec chown -h www-data {} \;
            find / -group $OLDGID -exec chgrp -h www-data {} \;
            if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]] && [ "$CELERYRUNNING" = false ]; then
                supervisorctl --serverurl http://localhost:9001 stop celery
            fi
            supervisorctl --serverurl http://localhost:9001 reread
            supervisorctl --serverurl http://localhost:9001 update
            if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]] && [ "$CELERYRUNNING" = false ]; then
                supervisorctl --serverurl http://localhost:9001 start celery
            fi
        fi
        echo "41.8" >&2
        if [ "${USEHTTPS:-false}" == "true" ]; then
            rm -f /etc/nginx/sites-enabled/docassemblehttp
            ln -sf /etc/nginx/sites-available/docassemblessl /etc/nginx/sites-enabled/docassemblessl
            if [ "${USELETSENCRYPT:-false}" == "true" ]; then
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
            rm -f /etc/letsencrypt/da_using_lets_encrypt
            rm -f /etc/nginx/sites-enabled/docassemblessl
            ln -sf /etc/nginx/sites-available/docassemblehttp /etc/nginx/sites-enabled/docassemblehttp
        fi
    fi
    echo "41.9" >&2
    backup_nginx

    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
        supervisorctl --serverurl http://localhost:9001 start websockets
    fi

    echo "46" >&2

    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
        supervisorctl --serverurl http://localhost:9001 start uwsgi
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]]; then
        if [ "$NGINXRUNNING" = false ]; then
            supervisorctl --serverurl http://localhost:9001 start nginx
        fi
    fi
fi

echo "42.9" >&2

if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then

    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [ "$APACHERUNNING" = false ]; then
        rm -f /etc/apache2/ports.conf
    fi

    function backup_apache {
        if [ "${S3ENABLE:-false}" == "true" ]; then
            if [ "${USELETSENCRYPT:-false}" == "true" ]; then
                cd /
                rm -f /tmp/letsencrypt.tar.gz
                if [ -d etc/letsencrypt ]; then
                    tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
                    s4cmd -f put /tmp/letsencrypt.tar.gz "s3://${S3BUCKET}/letsencrypt.tar.gz"
                    rm -f /tmp/letsencrypt.tar.gz
                fi
            fi
            if [[ $CONTAINERROLE =~ .*:(all):.* ]] || [[ ! $(python -m docassemble.webapp.list-cloud apache) ]]; then
                s4cmd dsync "/etc/apache2/sites-available" "s3://${S3BUCKET}/apache"
            fi
        elif [ "${AZUREENABLE:-false}" == "true" ]; then
            if [ "${USELETSENCRYPT:-false}" == "true" ]; then
                cd /
                rm -f /tmp/letsencrypt.tar.gz
                if [ -d etc/letsencrypt ]; then
                    tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
                    echo "Saving lets encrypt" >&2
                    cmd_retry blob-cmd -f cp /tmp/letsencrypt.tar.gz "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/letsencrypt.tar.gz"
                    rm -f /tmp/letsencrypt.tar.gz
                fi
            fi
            if [[ $CONTAINERROLE =~ .*:(all):.* ]] || [[ ! $(python -m docassemble.webapp.list-cloud apache) ]]; then
                for the_file in $(find /etc/apache2/sites-available/ -type f); do
                    target_file=`basename "${the_file}"`
                    echo "Saving apache" >&2
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
                rm -rf "${DA_ROOT}/backup/apache"
                mkdir -p "${DA_ROOT}/backup/apache"
                rsync -auq /etc/apache2/sites-available/ "${DA_ROOT}/backup/apache/"
            fi
        fi
    }

    echo "43" >&2

    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [ "$APACHERUNNING" = false ]; then
        echo "Listen 80" > /etc/apache2/ports.conf
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
            OLDUID=`id -u www-data`
            OLDGID=`id -g www-data`

            usermod -o -u $WWWUID www-data
            groupmod -o -g $WWWGID www-data
            find / -user $OLDUID -exec chown -h www-data {} \;
            find / -group $OLDGID -exec chgrp -h www-data {} \;
            if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]] && [ "$CELERYRUNNING" = false ]; then
                supervisorctl --serverurl http://localhost:9001 stop celery
            fi
            supervisorctl --serverurl http://localhost:9001 reread
            supervisorctl --serverurl http://localhost:9001 update
            if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]] && [ "$CELERYRUNNING" = false ]; then
                supervisorctl --serverurl http://localhost:9001 start celery
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
        echo -e "Timeout ${DATIMEOUT:-60}\nDefine DAHOSTNAME ${DAHOSTNAME}\nDefine DAPOSTURLROOT ${POSTURLROOT}\nDefine DAWSGIROOT ${WSGIROOT}\nDefine DASERVERADMIN ${SERVERADMIN}\nDefine DAWEBSOCKETSIP ${DAWEBSOCKETSIP}\nDefine DAWEBSOCKETSPORT ${DAWEBSOCKETSPORT}\nDefine DACROSSSITEDOMAINVALUE *" >> /etc/apache2/conf-available/docassemble.conf
        if [ "${BEHINDHTTPSLOADBALANCER:-false}" == "true" ]; then
            echo "Listen 8081" >> /etc/apache2/ports.conf
            a2ensite docassemble-redirect
        fi
        if [ "${USEHTTPS:-false}" == "true" ]; then
            echo "Listen 443" >> /etc/apache2/ports.conf
            a2enmod ssl
            a2ensite docassemble-ssl
            if [ "${USELETSENCRYPT:-false}" == "true" ]; then
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
            rm -f /etc/letsencrypt/da_using_lets_encrypt
            a2dismod ssl
            a2dissite -q docassemble-ssl &> /dev/null
        fi
        backup_apache
    fi

    echo "44" >&2

    if [[ $CONTAINERROLE =~ .*:(log):.* ]] && [ "$APACHERUNNING" = false ]; then
        echo "Listen 8080" >> /etc/apache2/ports.conf
        a2enmod cgid
        a2ensite docassemble-log
    fi

    echo "45" >&2

    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
        supervisorctl --serverurl http://localhost:9001 start websockets
    fi

    echo "46" >&2

    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [ "$APACHERUNNING" = false ]; then
        supervisorctl --serverurl http://localhost:9001 start apache2
    fi
fi

echo "47" >&2

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
    if [ "${USEHTTPS:-false}" == "false" ]; then
        curl -s http://localhost/ > /dev/null
    else
        curl -s -k https://localhost/ > /dev/null
    fi
    if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
        if [ "$APACHERUNNING" = false ]; then
            supervisorctl --serverurl http://localhost:9001 stop apache2
            supervisorctl --serverurl http://localhost:9001 start apache2
        fi
    fi
fi

echo "48" >&2

su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.webapp.register \"${DA_CONFIG_FILE}\"" www-data

echo "49" >&2

if [ "$CRONRUNNING" = false ]; then
    if ! grep -q '^CONTAINERROLE' /etc/crontab; then
        bash -c "set | grep -e '^CONTAINERROLE=' -e '^DA_PYTHON=' -e '^DA_CONFIG=' -e '^DA_ROOT=' -e '^DAPYTHONVERSION='; cat /etc/crontab" > /tmp/crontab && cat /tmp/crontab > /etc/crontab && rm -f /tmp/crontab
    fi
    supervisorctl --serverurl http://localhost:9001 start cron
fi

echo "50" >&2

if [[ $CONTAINERROLE =~ .*:(all|mail):.* && ($DBTYPE = "postgresql" || $DBTYPE = "mysql") ]]; then
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

echo "51" >&2

if [[ $CONTAINERROLE =~ .*:(log):.* ]] || [ "$OTHERLOGSERVER" = true ]; then
    if [ -d /etc/syslog-ng ]; then
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
            let LOGDIRECTORYLENGTH=${#LOGDIRECTORY}+2
            for the_file in $(find "${LOGDIRECTORY}" -type f | cut -c ${LOGDIRECTORYLENGTH}-); do
                echo "Saving log file $the_file" >&2
                cmd_retry blob-cmd -f cp "${LOGDIRECTORY}/${the_file}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/log/${the_file}"
            done
        fi
        if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
            if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
                for the_file in $(find /var/log/apache2 -type f | cut -c 18-); do
                    echo "Saving log file $the_file" >&2
                    cmd_retry blob-cmd -f cp "/var/log/apache2/${the_file}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/apachelogs/${the_file}"
                done
            fi
            if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
                for the_file in $(find /var/log/nginx -type f | cut -c 16-); do
                    echo "Saving log file $the_file" >&2
                    cmd_retry blob-cmd -f cp "/var/log/nginx/${the_file}" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/nginxlogs/${the_file}"
                done
            fi
        fi
    else
        if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
            if [ "${DAWEBSERVER:-nginx}" = "apache" ]; then
                rm -rf "${DA_ROOT}/backup/apachelogs"
                mkdir -p "${DA_ROOT}/backup/apachelogs"
                rsync -auq /var/log/apache2/ "${DA_ROOT}/backup/apachelogs/"
            fi
            if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
                rm -rf "${DA_ROOT}/backup/nginxlogs"
                mkdir -p "${DA_ROOT}/backup/nginxlogs"
                rsync -auq /var/log/nginx/ "${DA_ROOT}/backup/nginxlogs/"
            fi
        fi
        if [[ $CONTAINERROLE =~ .*:(all|log):.* ]]; then
            rm -rf "${DA_ROOT}/backup/log"
            rsync -auq "${LOGDIRECTORY}/" "${DA_ROOT}/backup/log/"
        fi
        if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
            rm -f "${DA_ROOT}/backup/config.yml"
            cp "${DA_CONFIG_FILE}" "${DA_ROOT}/backup/config.yml"
            rm -rf "${DA_ROOT}/backup/files"
            rsync -auq "${DA_ROOT}/files" "${DA_ROOT}/backup/"
        fi
    fi
    echo "finished shutting down initialize" >&2
    kill %1
    exit 0
}

trap deregister SIGINT SIGTERM

echo "initialize finished" >&2
touch "${DA_ROOT}/webapp/ready"
sleep infinity &
wait %1
