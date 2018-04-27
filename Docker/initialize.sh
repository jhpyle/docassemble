#! /bin/bash

export HOME=/root
export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/local}/bin/activate"
echo "Activating with ${DA_ACTIVATE}"
source $DA_ACTIVATE

export DA_CONFIG_FILE_DIST="${DA_CONFIG_FILE_DIST:-${DA_ROOT}/config/config.yml.dist}"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
export CONTAINERROLE=":${CONTAINERROLE:-all}:"

if pg_isready -q; then
    PGRUNNING=true
else
    PGRUNNING=false
fi

export DEBIAN_FRONTEND=noninteractive
apt-get clean &> /dev/null
#apt-get -q -y update &> /dev/null
#apt-get -q -y install libsasl2-dev libldap2-dev &> /dev/null
su -c "source $DA_ACTIVATE && pip install python-ldap &> /dev/null" www-data

# echo "1"

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

# echo "2"

if redis-cli ping &> /dev/null; then
    REDISRUNNING=true
else
    REDISRUNNING=false
fi

# echo "3"

if rabbitmqctl status &> /dev/null; then
    RABBITMQRUNNING=true
else
    RABBITMQRUNNING=false
fi

# echo "4"

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

# echo "5"

if [ "${USEHTTPS:-false}" == "false" ] && [ "${BEHINDHTTPSLOADBALANCER:-false}" == "false" ]; then
    URLROOT="http:\\/\\/"
else
    URLROOT="https:\\/\\/"
fi

# echo "6"

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

# echo "7"

if [ "${S3ENABLE:-null}" == "null" ] && [ "${S3BUCKET:-null}" != "null" ]; then
    export S3ENABLE=true
fi

# echo "8"

if [ "${S3ENABLE:-null}" == "true" ] && [ "${S3BUCKET:-null}" != "null" ] && [ "${S3ACCESSKEY:-null}" != "null" ] && [ "${S3SECRETACCESSKEY:-null}" != "null" ]; then
    export AWS_ACCESS_KEY_ID=$S3ACCESSKEY
    export AWS_SECRET_ACCESS_KEY=$S3SECRETACCESSKEY
fi

# echo "9"

if [ "${AZUREENABLE:-null}" == "null" ] && [ "${AZUREACCOUNTNAME:-null}" != "null" ] && [ "${AZUREACCOUNTKEY:-null}" != "null" ] && [ "${AZURECONTAINER:-null}" != "null" ]; then
    export AZUREENABLE=true
fi

# echo "10"

if [ "${S3ENABLE:-false}" == "true" ] && [[ $CONTAINERROLE =~ .*:(web):.* ]] && [[ $(s3cmd ls s3://${S3BUCKET}/hostname-rabbitmq) ]] && [[ $(s3cmd ls s3://${S3BUCKET}/ip-rabbitmq) ]]; then
    TEMPKEYFILE=`mktemp`
    s3cmd -q -f get s3://${S3BUCKET}/hostname-rabbitmq $TEMPKEYFILE
    HOSTNAMERABBITMQ=$(<$TEMPKEYFILE)
    s3cmd -q -f get s3://${S3BUCKET}/ip-rabbitmq $TEMPKEYFILE
    IPRABBITMQ=$(<$TEMPKEYFILE)
    rm -f $TEMPKEYFILE
    if [ -n "$(grep $HOSTNAMERABBITMQ /etc/hosts)" ]; then
	sed -i "/$HOSTNAMERABBITMQ/d" /etc/hosts
    fi
    echo "$IPRABBITMQ $HOSTNAMERABBITMQ" >> /etc/hosts
fi

# echo "11"

if [ "${AZUREENABLE:-false}" == "true" ]; then
    echo "Initializing azure" >&2
    blob-cmd -f -v add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
fi

# echo "12"

if [ "${AZUREENABLE:-false}" == "true" ] && [[ $CONTAINERROLE =~ .*:(web):.* ]] && [[ $(python -m docassemble.webapp.list-cloud hostname-rabbitmq) ]] && [[ $(python -m docassemble.webapp.list-cloud ip-rabbitmq) ]]; then
    TEMPKEYFILE=`mktemp`
    echo "Copying hostname-rabbitmq" >&2
    blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/hostname-rabbitmq" $TEMPKEYFILE
    HOSTNAMERABBITMQ=$(<$TEMPKEYFILE)
    echo "Copying ip-rabbitmq" >&2
    blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/ip-rabbitmq" $TEMPKEYFILE
    IPRABBITMQ=$(<$TEMPKEYFILE)
    rm -f $TEMPKEYFILE
    if [ -n "$(grep $HOSTNAMERABBITMQ /etc/hosts)" ]; then
	sed -i "/$HOSTNAMERABBITMQ/d" /etc/hosts
    fi
    echo "$IPRABBITMQ $HOSTNAMERABBITMQ" >> /etc/hosts
fi

# echo "13"

if [ "${S3ENABLE:-false}" == "true" ]; then
    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [[ $(s3cmd ls s3://${S3BUCKET}/letsencrypt.tar.gz) ]]; then
	rm -f /tmp/letsencrypt.tar.gz
	s3cmd -q get s3://${S3BUCKET}/letsencrypt.tar.gz /tmp/letsencrypt.tar.gz
	cd /
	tar -xf /tmp/letsencrypt.tar.gz
	rm -f /tmp/letsencrypt.tar.gz
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [[ $(s3cmd ls s3://${S3BUCKET}/apache) ]]; then
	s3cmd -q sync s3://${S3BUCKET}/apache/ /etc/apache2/sites-available/
    fi
    if [[ $CONTAINERROLE =~ .*:(all|log):.* ]] && [[ $(s3cmd ls s3://${S3BUCKET}/log) ]]; then
	s3cmd -q sync s3://${S3BUCKET}/log/ ${LOGDIRECTORY:-${DA_ROOT}/log}/
	chown -R www-data.www-data ${LOGDIRECTORY:-${DA_ROOT}/log}
    fi
    if [[ $(s3cmd ls s3://${S3BUCKET}/config.yml) ]]; then
	rm -f $DA_CONFIG_FILE
	s3cmd -q get s3://${S3BUCKET}/config.yml $DA_CONFIG_FILE
	chown www-data.www-data $DA_CONFIG_FILE
    fi
    if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [[ $(s3cmd ls s3://${S3BUCKET}/redis.rdb) ]] && [ "$REDISRUNNING" = false ]; then
	s3cmd -q -f get s3://${S3BUCKET}/redis.rdb "/var/lib/redis/dump.rdb"
	chown redis.redis "/var/lib/redis/dump.rdb"
    fi
elif [ "${AZUREENABLE:-false}" == "true" ]; then
    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [[ $(python -m docassemble.webapp.list-cloud letsencrypt.tar.gz) ]]; then
	rm -f /tmp/letsencrypt.tar.gz
	echo "Copying let's encrypt" >&2
	blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/letsencrypt.tar.gz" "/tmp/letsencrypt.tar.gz"
	cd /
	tar -xf /tmp/letsencrypt.tar.gz
	rm -f /tmp/letsencrypt.tar.gz
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [[ $(python -m docassemble.webapp.list-cloud apache) ]]; then
	echo "There are apache files on Azure" >&2
	for the_file in $(python -m docassemble.webapp.list-cloud apache/); do
	    echo "Found $the_file on Azure" >&2
	    if ! [[ $the_file =~ /$ ]]; then
  	        target_file=`basename $the_file`
  		echo "Copying apache" >&2
	        blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/${the_file}" "/etc/apache2/sites-available/${target_file}"
	    fi
	done
    fi
    if [[ $CONTAINERROLE =~ .*:(all|log):.* ]] && [[ $(python -m docassemble.webapp.list-cloud log) ]]; then
	echo "There are log files on Azure" >&2
	for the_file in $(python -m docassemble.webapp.list-cloud log/); do
	    echo "Found $the_file on Azure" >&2
	    if ! [[ $the_file =~ /$ ]]; then
	        target_file=`basename $the_file`
  		echo "Copying log file $the_file" >&2
	        blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/${the_file}" "${LOGDIRECTORY:-${DA_ROOT}/log}/${target_file}"
	    fi
	done
	chown -R www-data.www-data ${LOGDIRECTORY:-${DA_ROOT}/log}
    fi
    if [[ $(python -m docassemble.webapp.list-cloud config.yml) ]]; then
	rm -f $DA_CONFIG_FILE
  	echo "Copying config.yml" >&2
	blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/config.yml" $DA_CONFIG_FILE
	chown www-data.www-data $DA_CONFIG_FILE
    fi
    if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [[ $(python -m docassemble.webapp.list-cloud redis.rdb) ]] && [ "$REDISRUNNING" = false ]; then
	echo "Copying redis" >&2
	blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/redis.rdb" "/var/lib/redis/dump.rdb"
	chown redis.redis "/var/lib/redis/dump.rdb"
    fi
else
    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [ -f ${DA_ROOT}/backup/letsencrypt.tar.gz ]; then
	cd /
	tar -xf ${DA_ROOT}/backup/letsencrypt.tar.gz
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [ -d ${DA_ROOT}/backup/apache ]; then
	rsync -auv ${DA_ROOT}/backup/apache/ /etc/apache2/sites-available/
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [ -d ${DA_ROOT}/backup/apachelogs ]; then
	rsync -auv ${DA_ROOT}/backup/apachelogs/ /var/log/apache2/
	chown root.adm /var/log/apache2/*
	chmod 640 /var/log/apache2/*
    fi
    if [[ $CONTAINERROLE =~ .*:(all|log):.* ]] && [ -d ${DA_ROOT}/backup/log ]; then
	rsync -auv ${DA_ROOT}/backup/log/ ${LOGDIRECTORY:-${DA_ROOT}}/log/
	chown -R www-data.www-data ${DA_ROOT}/log
    fi
    if [ -f ${DA_ROOT}/backup/config.yml ]; then
	cp ${DA_ROOT}/backup/config.yml $DA_CONFIG_FILE
	chown www-data.www-data $DA_CONFIG_FILE
    fi
    if [ -d ${DA_ROOT}/backup/files ]; then
	rsync -auv ${DA_ROOT}/backup/files ${DA_ROOT}/
	chown -R www-data.www-data ${DA_ROOT}/files
    fi
    if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [ -f ${DA_ROOT}/backup/redis.rdb ] && [ "$REDISRUNNING" = false ]; then
	cp ${DA_ROOT}/backup/redis.rdb /var/lib/redis/dump.rdb
	chown redis.redis "/var/lib/redis/dump.rdb"
    fi
fi

# echo "14"

DEFAULT_SECRET=$(python -m docassemble.base.generate_key)

# echo "15"

if [ ! -f $DA_CONFIG_FILE ]; then
    sed -e 's@{{DBPREFIX}}@'"${DBPREFIX:-postgresql+psycopg2:\/\/}"'@' \
	-e 's/{{DBNAME}}/'"${DBNAME:-docassemble}"'/' \
	-e 's/{{DBUSER}}/'"${DBUSER:-docassemble}"'/' \
	-e 's#{{DBPASSWORD}}#'"${DBPASSWORD:-abc123}"'#' \
	-e 's/{{DBHOST}}/'"${DBHOST:-null}"'/' \
	-e 's/{{DBPORT}}/'"${DBPORT:-null}"'/' \
	-e 's/{{DBTABLEPREFIX}}/'"${DBTABLEPREFIX:-null}"'/' \
	-e 's/{{S3ENABLE}}/'"${S3ENABLE:-false}"'/' \
	-e 's#{{S3ACCESSKEY}}#'"${S3ACCESSKEY:-null}"'#' \
	-e 's#{{S3SECRETACCESSKEY}}#'"${S3SECRETACCESSKEY:-null}"'#' \
	-e 's/{{S3BUCKET}}/'"${S3BUCKET:-null}"'/' \
	-e 's/{{S3REGION}}/'"${S3REGION:-null}"'/' \
	-e 's/{{AZUREENABLE}}/'"${AZUREENABLE:-false}"'/' \
	-e 's/{{AZUREACCOUNTNAME}}/'"${AZUREACCOUNTNAME:-null}"'/' \
	-e 's@{{AZUREACCOUNTKEY}}@'"${AZUREACCOUNTKEY:-null}"'@' \
	-e 's/{{AZURECONTAINER}}/'"${AZURECONTAINER:-null}"'/' \
	-e 's@{{REDIS}}@'"${REDIS:-null}"'@' \
	-e 's#{{RABBITMQ}}#'"${RABBITMQ:-null}"'#' \
	-e 's@{{TIMEZONE}}@'"${TIMEZONE:-null}"'@' \
	-e 's/{{EC2}}/'"${EC2:-false}"'/' \
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
	$DA_CONFIG_FILE_DIST > $DA_CONFIG_FILE || exit 1
fi
chown www-data.www-data $DA_CONFIG_FILE

# echo "16"

source /dev/stdin < <(su -c "source $DA_ACTIVATE && python -m docassemble.base.read_config $DA_CONFIG_FILE" www-data)

# echo "17"

if [ "${S3ENABLE:-false}" == "true" ] && [[ ! $(s3cmd ls s3://${S3BUCKET}/config.yml) ]]; then
    s3cmd -q put $DA_CONFIG_FILE s3://${S3BUCKET}/config.yml
fi

if [ "${S3ENABLE:-false}" == "true" ] && [[ ! $(s3cmd ls s3://${S3BUCKET}/files) ]]; then
    if [ -d ${DA_ROOT}/files ]; then
	for the_file in $(ls ${DA_ROOT}/files); do
	    if [[ $the_file =~ ^[0-9]+ ]]; then
		for sub_file in $(find ${DA_ROOT}/files/$the_file -type f); do
		    file_number=${sub_file#${DA_ROOT}/files/}
		    file_number=${file_number:0:15}
		    file_directory=${DA_ROOT}/files/$file_number
		    target_file=${sub_file#${file_directory}}
		    file_number=${file_number//\//}
		    file_number=$((16#$file_number))
		    s3cmd -q put $sub_file s3://${S3BUCKET}/files/$file_number/$target_file
		done
	    else
	       s3cmd -q sync ${DA_ROOT}/files/$the_file/ s3://${S3BUCKET}/$the_file/
	    fi
	done
    fi
fi
# echo "18"

if [ "${AZUREENABLE:-false}" == "true" ]; then
    echo "Initializing azure" >&2
    blob-cmd -f -v add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
fi

# echo "19"

if [ "${AZUREENABLE:-false}" == "true" ] && [[ ! $(python -m docassemble.webapp.list-cloud config.yml) ]]; then
    echo "Saving config" >&2
    blob-cmd -f cp $DA_CONFIG_FILE "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/config.yml"
fi

# echo "19.5"

if [ "${AZUREENABLE:-false}" == "true" ] && [[ ! $(python -m docassemble.webapp.list-cloud files) ]]; then
    if [ -d ${DA_ROOT}/files ]; then
	for the_file in $(ls ${DA_ROOT}/files); do
	    if [[ $the_file =~ ^[0-9]+ ]]; then
		for sub_file in $(find ${DA_ROOT}/files/$the_file -type f); do
		    file_number=${sub_file#${DA_ROOT}/files/}
		    file_number=${file_number:0:15}
		    file_directory=${DA_ROOT}/files/$file_number/
		    target_file=${sub_file#${file_directory}}
		    file_number=${file_number//\//}
		    file_number=$((16#$file_number))
		    echo blob-cmd -f cp $sub_file "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/files/$file_number/$target_file"
		done
	    else
		for sub_file in $(find ${DA_ROOT}/files/$the_file -type f); do
		    target_file=${sub_file#${DA_ROOT}/files/}
		    echo blob-cmd -f cp $sub_file "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/$target_file"
		done
	    fi
	done
    fi
fi

# echo "20"

if [ "${EC2:-false}" == "true" ]; then
    export LOCAL_HOSTNAME=`curl -s http://169.254.169.254/latest/meta-data/local-hostname`
    export PUBLIC_HOSTNAME=`curl -s http://169.254.169.254/latest/meta-data/public-hostname`
else
    export LOCAL_HOSTNAME=`hostname --fqdn`
    export PUBLIC_HOSTNAME=$LOCAL_HOSTNAME
fi

# echo "21"

if [ "${DAHOSTNAME:-none}" == "none" ]; then
    export DAHOSTNAME=$PUBLIC_HOSTNAME
fi

# echo "22"

if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]]; then
    a2dissite -q 000-default &> /dev/null
    a2dissite -q default-ssl &> /dev/null
    rm -f /etc/apache2/sites-available/000-default.conf
    rm -f /etc/apache2/sites-available/default-ssl.conf
    if [ "${DAHOSTNAME:-none}" != "none" ]; then
	if [ ! -f /etc/apache2/sites-available/docassemble-ssl.conf ]; then
	    cp ${DA_ROOT}/config/docassemble-ssl.conf.dist /etc/apache2/sites-available/docassemble-ssl.conf
	    rm -f /etc/letsencrypt/da_using_lets_encrypt
	fi
	if [ ! -f /etc/apache2/sites-available/docassemble-http.conf ]; then
	    cp ${DA_ROOT}/config/docassemble-http.conf.dist /etc/apache2/sites-available/docassemble-http.conf
	    rm -f /etc/letsencrypt/da_using_lets_encrypt
	fi
	if [ ! -f /etc/apache2/sites-available/docassemble-log.conf ]; then
	    cp ${DA_ROOT}/config/docassemble-log.conf.dist /etc/apache2/sites-available/docassemble-log.conf
	fi
	if [ ! -f /etc/apache2/sites-available/docassemble-redirect.conf ]; then
	    cp ${DA_ROOT}/config/docassemble-redirect.conf.dist /etc/apache2/sites-available/docassemble-redirect.conf
	fi
    else
	if [ ! -f /etc/apache2/sites-available/docassemble-http.conf ]; then
	    cp ${DA_ROOT}/config/docassemble-http.conf.dist /etc/apache2/sites-available/docassemble-http.conf || exit 1
	fi
    fi
    a2ensite docassemble-http
fi

# echo "23"

if [ "${LOCALE:-undefined}" == "undefined" ]; then
    LOCALE="en_US.UTF-8 UTF-8"
fi

# echo "24"

set -- $LOCALE
DA_LANGUAGE=$1
grep -q "^$LOCALE" /etc/locale.gen || { echo $LOCALE >> /etc/locale.gen && locale-gen ; }
update-locale LANG=$DA_LANGUAGE

# echo "25"

if [ -n "$OTHERLOCALES" ]; then
    NEWLOCALE=false
    for LOCALETOSET in "${OTHERLOCALES[@]}"; do
	grep -q "^$LOCALETOSET" /etc/locale.gen || { echo $LOCALETOSET >> /etc/locale.gen; NEWLOCALE=true; }
    done
    if [ "$NEWLOCALE" = true ]; then
	locale-gen
    fi
fi

# echo "26"

if [ -n "$PACKAGES" ]; then
    for PACKAGE in "${PACKAGES[@]}"; do
        apt-get -q -y install $PACKAGE &> /dev/null
    done
fi

# echo "27"

if [ "${TIMEZONE:-undefined}" != "undefined" ]; then
    echo $TIMEZONE > /etc/timezone
    dpkg-reconfigure -f noninteractive tzdata
fi

# echo "28"

if [ "${S3ENABLE:-false}" == "true" ] || [ "${AZUREENABLE:-false}" == "true" ]; then
    su -c "source $DA_ACTIVATE && python -m docassemble.webapp.cloud_register $DA_CONFIG_FILE" www-data
fi

# echo "29"

if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]] && [ "$PGRUNNING" = false ] && [ "$DBTYPE" == "postgresql" ]; then
    supervisorctl --serverurl http://localhost:9001 start postgres || exit 1
    sleep 4
    su -c "while ! pg_isready -q; do sleep 1; done" postgres
    roleexists=`su -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='${DBUSER:-docassemble}'\"" postgres`
    if [ -z "$roleexists" ]; then
	echo "create role "${DBUSER:-docassemble}" with login password '"${DBPASSWORD:-abc123}"';" | su -c psql postgres || exit 1
    fi
    if [ "${S3ENABLE:-false}" == "true" ] && [[ $(s3cmd ls s3://${S3BUCKET}/postgres) ]]; then
	PGBACKUPDIR=`mktemp -d`
	s3cmd -q sync s3://${S3BUCKET}/postgres/ "$PGBACKUPDIR/"
    elif [ "${AZUREENABLE:-false}" == "true" ] && [[ $(python -m docassemble.webapp.list-cloud postgres) ]]; then
	echo "There are postgres files on Azure" >&2
	PGBACKUPDIR=`mktemp -d`
	for the_file in $(python -m docassemble.webapp.list-cloud postgres/); do
	    echo "Found $the_file on Azure" >&2
	    if ! [[ $the_file =~ /$ ]]; then
  	        target_file=`basename $the_file`
		echo "Copying $the_file to $target_file" >&2
	        blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/${the_file}" "$PGBACKUPDIR/${target_file}"
	    fi
	done
    else
	PGBACKUPDIR=${DA_ROOT}/backup/postgres
    fi
    if [ -d $PGBACKUPDIR ]; then
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
	echo "create database "${DBNAME:-docassemble}" owner "${DBUSER:-docassemble}";" | su -c psql postgres || exit 1
    fi
fi

echo "30" >&2

if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    su -c "source $DA_ACTIVATE && python -m docassemble.webapp.fix_postgresql_tables $DA_CONFIG_FILE && python -m docassemble.webapp.create_tables $DA_CONFIG_FILE" www-data
fi

echo "31" >&2

if [ -f /etc/syslog-ng/syslog-ng.conf ] && [ ! -f ${DA_ROOT}/webapp/syslog-ng-orig.conf ]; then
    cp /etc/syslog-ng/syslog-ng.conf ${DA_ROOT}/webapp/syslog-ng-orig.conf
fi

# echo "32" >&2

OTHERLOGSERVER=false

if [[ $CONTAINERROLE =~ .*:(web|celery):.* ]]; then
    if [ "${LOGSERVER:-undefined}" != "undefined" ]; then
	OTHERLOGSERVER=true
    fi
fi

# echo "33" >&2

if [[ $CONTAINERROLE =~ .*:(log):.* ]] || [ "${LOGSERVER:-undefined}" == "null" ]; then
    OTHERLOGSERVER=false
fi

# echo "34" >&2

if [ "$OTHERLOGSERVER" = false ] && [ -f ${LOGDIRECTORY:-${DA_ROOT}/log}/docassemble.log ]; then
    chown www-data.www-data ${LOGDIRECTORY:-${DA_ROOT}/log}/docassemble.log
fi

# echo "35" >&2

if [[ $CONTAINERROLE =~ .*:(log):.* ]] || [ "$OTHERLOGSERVER" = true ]; then
    if [ -d /etc/syslog-ng ]; then
	if [ "$OTHERLOGSERVER" = true ]; then
	    cp ${DA_ROOT}/webapp/syslog-ng-docker.conf /etc/syslog-ng/syslog-ng.conf
	    cp ${DA_ROOT}/webapp/docassemble-syslog-ng.conf /etc/syslog-ng/conf.d/docassemble.conf
	else
	    rm -f /etc/syslog-ng/conf.d/docassemble.conf
	    cp ${DA_ROOT}/webapp/syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
	fi
	supervisorctl --serverurl http://localhost:9001 start syslogng
    fi
fi

echo "36" >&2

if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [ "$REDISRUNNING" = false ]; then
    supervisorctl --serverurl http://localhost:9001 start redis
fi

echo "37" >&2

if [[ $CONTAINERROLE =~ .*:(all|rabbitmq):.* ]] && [ "$RABBITMQRUNNING" = false ]; then
    supervisorctl --serverurl http://localhost:9001 start rabbitmq
fi

echo "38" >&2

su -c "source $DA_ACTIVATE && python -m docassemble.webapp.update $DA_CONFIG_FILE" www-data || exit 1

echo "39" >&2

if su -c "source $DA_ACTIVATE && celery -A docassemble.webapp.worker status" www-data 2>&1 | grep -q `hostname`; then
    CELERYRUNNING=true;
else
    CELERYRUNNING=false;
fi

echo "40" >&2

if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]] && [ "$CELERYRUNNING" = false ]; then
    supervisorctl --serverurl http://localhost:9001 start celery
fi

echo "41" >&2

if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [ "$APACHERUNNING" = false ]; then
    rm -f /etc/apache2/ports.conf
fi

echo "42" >&2

if [ ! -f ${DA_ROOT}/certs/apache.key ] && [ -f ${DA_ROOT}/certs/apache.key.orig ]; then
    mv ${DA_ROOT}/certs/apache.key.orig ${DA_ROOT}/certs/apache.key
fi
if [ ! -f ${DA_ROOT}/certs/apache.crt ] && [ -f ${DA_ROOT}/certs/apache.crt.orig ]; then
    mv ${DA_ROOT}/certs/apache.crt.orig ${DA_ROOT}/certs/apache.crt
fi
if [ ! -f ${DA_ROOT}/certs/apache.ca.pem ] && [ -f ${DA_ROOT}/certs/apache.ca.pem.orig ]; then
    mv ${DA_ROOT}/certs/apache.ca.pem.orig ${DA_ROOT}/certs/apache.ca.pem
fi
if [ ! -f ${DA_ROOT}/certs/exim.key ] && [ -f ${DA_ROOT}/certs/exim.key.orig ]; then
    mv ${DA_ROOT}/certs/exim.key.orig ${DA_ROOT}/certs/exim.key
fi
if [ ! -f ${DA_ROOT}/certs/exim.crt ] && [ -f ${DA_ROOT}/certs/exim.crt.orig ]; then
    mv ${DA_ROOT}/certs/exim.crt.orig ${DA_ROOT}/certs/exim.crt
fi
python -m docassemble.webapp.install_certs $DA_CONFIG_FILE || exit 1

echo "43" >&2

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [ "$APACHERUNNING" = false ]; then
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
    echo -e "# This file is automatically generated\nWSGIPythonHome ${DA_PYTHON:-${DA_ROOT}/local}\nTimeout ${DATIMEOUT:-60}\nDefine DAHOSTNAME ${DAHOSTNAME}\nDefine DAPOSTURLROOT ${POSTURLROOT}\nDefine DAWSGIROOT ${WSGIROOT}\nDefine DASERVERADMIN ${SERVERADMIN}" > /etc/apache2/conf-available/docassemble.conf
    if [ -n "${CROSSSITEDOMAIN}" ]; then
	echo "Define DACROSSSITEDOMAIN ${CROSSSITEDOMAIN}" >> /etc/apache2/conf-available/docassemble.conf
    fi
    echo "Listen 80" >> /etc/apache2/ports.conf
    if [ "${BEHINDHTTPSLOADBALANCER:-false}" == "true" ]; then
	echo "Listen 8081" >> /etc/apache2/ports.conf
	a2ensite docassemble-redirect
    fi
    if [ "${USEHTTPS:-false}" == "true" ]; then
	echo "Listen 443" >> /etc/apache2/ports.conf
	a2enmod ssl
	a2ensite docassemble-ssl
	if [ "${USELETSENCRYPT:-false}" == "true" ]; then
	    cd ${DA_ROOT}/letsencrypt 
	    if [ -f /etc/letsencrypt/da_using_lets_encrypt ]; then
		./letsencrypt-auto renew
	    else
		./letsencrypt-auto --apache --quiet --email ${LETSENCRYPTEMAIL} --agree-tos -d ${DAHOSTNAME} && touch /etc/letsencrypt/da_using_lets_encrypt
	    fi
	    cd ~-
	    /etc/init.d/apache2 stop
	else
	    rm -f /etc/letsencrypt/da_using_lets_encrypt
	fi
    else
	rm -f /etc/letsencrypt/da_using_lets_encrypt
	a2dismod ssl
	a2dissite -q docassemble-ssl &> /dev/null
    fi
    if [ "${S3ENABLE:-false}" == "true" ]; then
	if [ "${USELETSENCRYPT:-false}" == "true" ]; then
	    cd /
	    rm -f /tmp/letsencrypt.tar.gz
	    if [ -d etc/letsencrypt ]; then
		tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
		s3cmd -q put /tmp/letsencrypt.tar.gz 's3://'${S3BUCKET}/letsencrypt.tar.gz
		rm -f /tmp/letsencrypt.tar.gz
	    fi
	fi
	s3cmd -q sync /etc/apache2/sites-available/ 's3://'${S3BUCKET}/apache/
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	if [ "${USELETSENCRYPT:-false}" == "true" ]; then
	    cd /
	    rm -f /tmp/letsencrypt.tar.gz
	    if [ -d etc/letsencrypt ]; then
		tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
		echo "Saving let's encrypt" >&2
		blob-cmd -f cp /tmp/letsencrypt.tar.gz "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/letsencrypt.tar.gz"
		rm -f /tmp/letsencrypt.tar.gz
	    fi
	fi
	for the_file in $(find /etc/apache2/sites-available/ -type f); do
	    target_file=`basename $the_file`
	    echo "Saving apache" >&2
	    blob-cmd -f cp $the_file "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/apache/$target_file" 
	done
    else
	if [ "${USELETSENCRYPT:-false}" == "true" ]; then
	    cd /
	    rm -f ${DA_ROOT}/backup/letsencrypt.tar.gz
	    tar -zcf ${DA_ROOT}/backup/letsencrypt.tar.gz etc/letsencrypt
	fi
	rm -rf ${DA_ROOT}/backup/apache
	mkdir -p ${DA_ROOT}/backup/apache
	rsync -auv /etc/apache2/sites-available/ ${DA_ROOT}/backup/apache/
    fi
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

echo "47" >&2

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
    if [ "${USEHTTPS:-false}" == "false" ]; then
	curl -s http://localhost/ > /dev/null
    else
	curl -s -k https://localhost/ > /dev/null
    fi
    if [ "$APACHERUNNING" = false ]; then
	supervisorctl --serverurl http://localhost:9001 stop apache2
	supervisorctl --serverurl http://localhost:9001 start apache2
    fi
fi

echo "48" >&2

su -c "source $DA_ACTIVATE && python -m docassemble.webapp.register $DA_CONFIG_FILE" www-data

echo "49" >&2

if [ "$CRONRUNNING" = false ]; then
    if ! grep -q '^CONTAINERROLE' /etc/crontab; then
	bash -c "set | grep -e '^CONTAINERROLE=' -e '^DA_PYTHON=' -e '^DA_CONFIG=' -e '^DA_ROOT='; cat /etc/crontab" > /tmp/crontab && cat /tmp/crontab > /etc/crontab && rm -f /tmp/crontab
    fi
    supervisorctl --serverurl http://localhost:9001 start cron
fi

echo "50" >&2

if [[ $CONTAINERROLE =~ .*:(all|mail):.* && ($DBTYPE = "postgresql" || $DBTYPE = "mysql") ]]; then
    if [ "${DBTYPE}" = "postgresql" ]; then
	cp ${DA_ROOT}/config/exim4-router-postgresql /etc/exim4/dbrouter
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
	cp ${DA_ROOT}/config/exim4-router-mysql /etc/exim4/dbrouter
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
    elif [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [ "${USELETSENCRYPT:-false}" == "true" ] && [ -f /etc/letsencrypt/live/${DAHOSTNAME}/cert.pem ] && [ -f /etc/letsencrypt/live/${DAHOSTNAME}/privkey.pem ]; then
	cp /etc/letsencrypt/live/${DAHOSTNAME}/fullchain.pem /etc/exim4/exim.crt
	cp /etc/letsencrypt/live/${DAHOSTNAME}/privkey.pem /etc/exim4/exim.key
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

function deregister {
    su -c "source $DA_ACTIVATE && python -m docassemble.webapp.deregister $DA_CONFIG_FILE" www-data
    if [ "${S3ENABLE:-false}" == "true" ]; then
	su -c "source $DA_ACTIVATE && python -m docassemble.webapp.cloud_deregister" www-data 
	if [[ $CONTAINERROLE =~ .*:(all|log):.* ]]; then
	    s3cmd -q sync ${DA_ROOT}/log/ s3://${S3BUCKET}/log/
	fi
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	su -c "source $DA_ACTIVATE && python -m docassemble.webapp.cloud_deregister" www-data 
	if [[ $CONTAINERROLE =~ .*:(all|log):.* ]]; then
	    for the_file in $(find ${DA_ROOT}/log -type f | cut -c 28-); do
		echo "Saving log file $the_file" >&2
		blob-cmd -f cp "${DA_ROOT}/log/$the_file" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/log/$target_file" 
	    done
	fi
    else
	if [[ $CONTAINERROLE =~ .*:(all|log):.* ]]; then
	    rm -rf ${DA_ROOT}/backup/log
	    rsync -auv ${DA_ROOT}/log ${DA_ROOT}/backup/
	    rm -rf ${DA_ROOT}/backup/apachelogs
	    mkdir -p ${DA_ROOT}/backup/apachelogs
	    rsync -auv /var/log/apache2/ ${DA_ROOT}/backup/apachelogs/
	fi
	rm -f ${DA_ROOT}/backup/config.yml
	cp $DA_CONFIG_FILE ${DA_ROOT}/backup/config.yml
	rm -rf ${DA_ROOT}/backup/files
	rsync -auv ${DA_ROOT}/files ${DA_ROOT}/backup/
    fi
    echo "finished shutting down initialize" >&2
    kill %1
    exit 0
}

trap deregister SIGINT SIGTERM

echo "initialize finished" >&2
sleep infinity &
wait %1
