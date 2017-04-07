#! /bin/bash

export HOME=/root
export DA_ACTIVATE="${DA_PYTHON:-/usr/share/docassemble/local}/bin/activate"
source $DA_ACTIVATE

export DA_CONFIG_FILE_DIST="${DA_CONFIG_FILE_DIST:-/usr/share/docassemble/config/config.yml.dist}"
export DA_CONFIG_FILE="${DA_CONFIG:-/usr/share/docassemble/config/config.yml}"
export CONTAINERROLE=":${CONTAINERROLE:-all}:"

if pg_isready -q; then
    PGRUNNING=true
else
    PGRUNNING=false
fi

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

if redis-cli ping &> /dev/null; then
    REDISRUNNING=true
else
    REDISRUNNING=false
fi

if rabbitmqctl status &> /dev/null; then
    RABBITMQRUNNING=true
else
    RABBITMQRUNNING=false
fi

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
    
if [ "${S3ENABLE:-null}" == "null" ] && [ "${S3BUCKET:-null}" != "null" ]; then
    export S3ENABLE=true
fi

if [ "${S3ENABLE:-null}" == "true" ] && [ "${S3BUCKET:-null}" != "null" ] && [ "${S3ACCESSKEY:-null}" != "null" ] && [ "${S3SECRETACCESSKEY:-null}" != "null" ]; then
    export AWS_ACCESS_KEY_ID=$S3ACCESSKEY
    export AWS_SECRET_ACCESS_KEY=$S3SECRETACCESSKEY
fi

if [ "${AZUREENABLE:-null}" == "null" ] && [ "${AZUREACCOUNTNAME:-null}" != "null" ] && [ "${AZUREACCOUNTKEY:-null}" != "null" ] && [ "${AZURECONTAINER:-null}" != "null" ]; then
    export AZUREENABLE=true
fi

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

if [ "${AZUREENABLE:-false}" == "true" ]; then
    blob-cmd -f -v add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
fi

if [ "${AZUREENABLE:-false}" == "true" ] && [[ $CONTAINERROLE =~ .*:(web):.* ]] && [[ $(python -m docassemble.webapp.list-cloud hostname-rabbitmq) ]] && [[ $(python -m docassemble.webapp.list-cloud hostname-rabbitmq ip-rabbitmq) ]]; then
    TEMPKEYFILE=`mktemp`
    blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/hostname-rabbitmq" $TEMPKEYFILE
    HOSTNAMERABBITMQ=$(<$TEMPKEYFILE)
    blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/ip-rabbitmq" $TEMPKEYFILE
    IPRABBITMQ=$(<$TEMPKEYFILE)
    rm -f $TEMPKEYFILE
    if [ -n "$(grep $HOSTNAMERABBITMQ /etc/hosts)" ]; then
	sed -i "/$HOSTNAMERABBITMQ/d" /etc/hosts
    fi
    echo "$IPRABBITMQ $HOSTNAMERABBITMQ" >> /etc/hosts
fi

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
	s3cmd -q sync s3://${S3BUCKET}/log/ ${LOGDIRECTORY:-/usr/share/docassemble/log}/
	chown -R www-data.www-data ${LOGDIRECTORY:-/usr/share/docassemble/log}
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
	blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/letsencrypt.tar.gz" "/tmp/letsencrypt.tar.gz"
	cd /
	tar -xf /tmp/letsencrypt.tar.gz
	rm -f /tmp/letsencrypt.tar.gz
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [[ $(python -m docassemble.webapp.list-cloud apache) ]]; then
	for the_file in $(python -m docassemble.webapp.list-cloud apache/); do
	    if ! [[ $the_file =~ /$ ]]; then
  	        target_file=`basename $the_file`
	        blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/$the_file" "/etc/apache2/sites-available/${target_file}"
	    fi
	done
    fi
    if [[ $CONTAINERROLE =~ .*:(all|log):.* ]] && [[ $(python -m docassemble.webapp.list-cloud log) ]]; then
	for the_file in $(python -m docassemble.webapp.list-cloud log/); do
	    if ! [[ $the_file =~ /$ ]]; then
	        target_file=`basename $the_file`
	        blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/$the_file" "${LOGDIRECTORY:-/usr/share/docassemble/log}/${target_file}"
	    fi
	done
	chown -R www-data.www-data ${LOGDIRECTORY:-/usr/share/docassemble/log}
    fi
    if [[ $(python -m docassemble.webapp.list-cloud config.yml) ]]; then
	rm -f $DA_CONFIG_FILE
	blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/config.yml" $DA_CONFIG_FILE
	chown www-data.www-data $DA_CONFIG_FILE
    fi
    if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [[ $(python -m docassemble.webapp.list-cloud redis.rdb) ]] && [ "$REDISRUNNING" = false ]; then
	blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/redis.rdb" "/var/lib/redis/dump.rdb"
	chown redis.redis "/var/lib/redis/dump.rdb"
    fi
else
    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [ -f /usr/share/docassemble/backup/letsencrypt.tar.gz ]; then
	cd /
	tar -xf /usr/share/docassemble/backup/letsencrypt.tar.gz
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [ -d /usr/share/docassemble/backup/apache ]; then
	cp -r /usr/share/docassemble/backup/apache/* /etc/apache2/sites-available/
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [ -d /usr/share/docassemble/backup/apachelogs ]; then
	cp -r /usr/share/docassemble/backup/apachelogs/* /var/log/apache2/
	chown root.adm /var/log/apache2/*
	chmod 640 /var/log/apache2/*
    fi
    if [[ $CONTAINERROLE =~ .*:(all|log):.* ]] && [ -d /usr/share/docassemble/backup/log ]; then
	cp -r /usr/share/docassemble/backup/log/* ${LOGDIRECTORY:-/usr/share/docassemble/log}/
	chown -R www-data.www-data /usr/share/docassemble/log
    fi
    if [ -f /usr/share/docassemble/backup/config.yml ]; then
	cp /usr/share/docassemble/backup/config.yml $DA_CONFIG_FILE
	chown www-data.www-data $DA_CONFIG_FILE
    fi
    if [ -d /usr/share/docassemble/backup/files ]; then
	cp -r /usr/share/docassemble/backup/files /usr/share/docassemble/
	chown -R www-data.www-data /usr/share/docassemble/files
    fi
    if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [ -f /usr/share/docassemble/backup/redis.rdb ] && [ "$REDISRUNNING" = false ]; then
	cp /usr/share/docassemble/backup/redis.rdb /var/lib/redis/dump.rdb
	chown redis.redis "/var/lib/redis/dump.rdb"
    fi
fi

DEFAULT_SECRET=$(python -m docassemble.base.generate_key)

if [ ! -f $DA_CONFIG_FILE ]; then
    sed -e 's@{{DBPREFIX}}@'"${DBPREFIX:-postgresql+psycopg2://}"'@' \
	-e 's/{{DBNAME}}/'"${DBNAME:-docassemble}"'/' \
	-e 's/{{DBUSER}}/'"${DBUSER:-docassemble}"'/' \
	-e 's/{{DBPASSWORD}}/'"${DBPASSWORD:-abc123}"'/' \
	-e 's/{{DBHOST}}/'"${DBHOST:-null}"'/' \
	-e 's/{{DBPORT}}/'"${DBPORT:-null}"'/' \
	-e 's/{{DBTABLEPREFIX}}/'"${DBTABLEPREFIX:-null}"'/' \
	-e 's/{{S3ENABLE}}/'"${S3ENABLE:-false}"'/' \
	-e 's/{{S3ACCESSKEY}}/'"${S3ACCESSKEY:-null}"'/' \
	-e 's/{{S3SECRETACCESSKEY}}/'"${S3SECRETACCESSKEY:-null}"'/' \
	-e 's/{{S3BUCKET}}/'"${S3BUCKET:-null}"'/' \
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
	-e 's/{{LOGSERVER}}/'"${LOGSERVER:-null}"'/' \
	-e 's/{{DAHOSTNAME}}/'"${DAHOSTNAME:-null}"'/' \
	-e 's/{{LOCALE}}/'"${LOCALE:-null}"'/' \
	-e 's/{{DASECRETKEY}}/'"${DEFAULT_SECRET}"'/' \
	-e 's@{{URLROOT}}@'"${URLROOT:-null}"'@' \
	-e 's/{{BEHINDHTTPSLOADBALANCER}}/'"${BEHINDHTTPSLOADBALANCER:-false}"'/' \
	$DA_CONFIG_FILE_DIST > $DA_CONFIG_FILE || exit 1
fi
chown www-data.www-data $DA_CONFIG_FILE

source /dev/stdin < <(su -c "source $DA_ACTIVATE && python -m docassemble.base.read_config $DA_CONFIG_FILE" www-data)

if [ "${S3ENABLE:-false}" == "true" ] && [[ ! $(s3cmd ls s3://${S3BUCKET}/config.yml) ]]; then
    s3cmd -q put $DA_CONFIG_FILE s3://${S3BUCKET}/config.yml
fi

if [ "${AZUREENABLE:-false}" == "true" ]; then
    blob-cmd -f -v add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
fi

if [ "${AZUREENABLE:-false}" == "true" ] && [[ ! $(python -m docassemble.webapp.list-cloud config.yml) ]]; then
    blob-cmd -f cp $DA_CONFIG_FILE "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/config.yml"
fi

if [ "${EC2:-false}" == "true" ]; then
    export LOCAL_HOSTNAME=`curl -s http://169.254.169.254/latest/meta-data/local-hostname`
    export PUBLIC_HOSTNAME=`curl -s http://169.254.169.254/latest/meta-data/public-hostname`
else
    export LOCAL_HOSTNAME=`hostname --fqdn`
    export PUBLIC_HOSTNAME=$LOCAL_HOSTNAME
fi

if [ "${DAHOSTNAME:-none}" == "none" ]; then
    export DAHOSTNAME=$PUBLIC_HOSTNAME
fi

if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]]; then
    rm -f /etc/apache2/sites-available/000-default.conf
    rm -f /etc/apache2/sites-available/default-ssl.conf
    a2dissite -q 000-default &> /dev/null
    a2dissite -q default-ssl &> /dev/null
    if [ "${DAHOSTNAME:-none}" != "none" ]; then
	if [ ! -f /etc/apache2/sites-available/docassemble-ssl.conf ] || [ "${USELETSENCRYPT:-none}" == "none" ] || [ "${USEHTTPS:-false}" == "false" ]; then
	    sed -e 's/#ServerName {{DAHOSTNAME}}/ServerName '"${DAHOSTNAME}"'/' \
		/usr/share/docassemble/config/docassemble-ssl.conf.dist > /etc/apache2/sites-available/docassemble-ssl.conf || exit 1
	    rm -f /etc/letsencrypt/da_using_lets_encrypt
	fi
	if [ ! -f /etc/apache2/sites-available/docassemble-http.conf ] || [ "${USELETSENCRYPT:-none}" == "none" ] || [ "${USEHTTPS:-false}" == "false" ]; then
	    sed -e 's/#ServerName {{DAHOSTNAME}}/ServerName '"${DAHOSTNAME}"'/' \
		/usr/share/docassemble/config/docassemble-http.conf.dist > /etc/apache2/sites-available/docassemble-http.conf || exit 1
	    rm -f /etc/letsencrypt/da_using_lets_encrypt
	fi
	if [ ! -f /etc/apache2/sites-available/docassemble-log.conf ]; then
	    sed -e 's/#ServerName {{DAHOSTNAME}}/ServerName '"${DAHOSTNAME}"'/' \
		/usr/share/docassemble/config/docassemble-log.conf.dist > /etc/apache2/sites-available/docassemble-log.conf || exit 1
	fi
	if [ ! -f /etc/apache2/sites-available/docassemble-redirect.conf ]; then
	    sed -e 's/#ServerName {{DAHOSTNAME}}/ServerName '"${DAHOSTNAME}"'/' \
		/usr/share/docassemble/config/docassemble-redirect.conf.dist > /etc/apache2/sites-available/docassemble-redirect.conf || exit 1
	fi
    else
	cp /usr/share/docassemble/config/docassemble-http.conf.dist /etc/apache2/sites-available/docassemble-http.conf || exit 1
    fi
    a2ensite docassemble-http
fi

if [ "${LOCALE:-undefined}" == "undefined" ]; then
    LOCALE="en_US.UTF-8 UTF-8"
fi

set -- $LOCALE
DA_LANGUAGE=$1
grep -q "^$LOCALE" /etc/locale.gen || { echo $LOCALE >> /etc/locale.gen && locale-gen ; }
update-locale LANG=$DA_LANGUAGE

if [ -n "$OTHERLOCALES" ]; then
    NEWLOCALE=false
    for LOCALETOSET in "${OTHERLOCALES[@]}"; do
	grep -q "^$LOCALETOSET" /etc/locale.gen || { echo $LOCALETOSET >> /etc/locale.gen; NEWLOCALE=true; }
    done
    if [ "$NEWLOCALE" = true ]; then
	locale-gen
    fi
fi

if [ -n "$PACKAGES" ]; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get clean
    apt-get update
    for PACKAGE in "${PACKAGES[@]}"; do
	apt-get -q -y install $PACKAGE
    done
fi

if [ "${TIMEZONE:-undefined}" != "undefined" ]; then
    echo $TIMEZONE > /etc/timezone
    dpkg-reconfigure -f noninteractive tzdata
fi

if [ "${S3ENABLE:-false}" == "true" ] || [ "${AZUREENABLE:-false}" == "true" ]; then
    su -c "source $DA_ACTIVATE && python -m docassemble.webapp.cloud_register $DA_CONFIG_FILE" www-data
fi

if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]] && [ "$PGRUNNING" = false ]; then
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
	PGBACKUPDIR=`mktemp -d`
	for the_file in $(python -m docassemble.webapp.list-cloud postgres/); do
	    if ! [[ $the_file =~ /$ ]]; then
  	        target_file=`basename $the_file`
	        blob-cmd -f cp "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/$the_file" "$PGBACKUPDIR/${target_file}"
	    fi
	done
    else
	PGBACKUPDIR=/usr/share/docassemble/backup/postgres
    fi
    if [ -d $PGBACKUPDIR ]; then
	cd "$PGBACKUPDIR"
	chown -R postgres.postgres "$PGBACKUPDIR"
	for db in $( ls ); do
	    pg_restore -F c -C -c $db | su -c psql postgres
	done
    fi
    dbexists=`su -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='${DBNAME:-docassemble}'\"" postgres`
    if [ -z "$dbexists" ]; then
	echo "create database "${DBNAME:-docassemble}" owner "${DBUSER:-docassemble}";" | su -c psql postgres || exit 1
    fi
fi

if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    su -c "source $DA_ACTIVATE && python -m docassemble.webapp.fix_postgresql_tables $DA_CONFIG_FILE && python -m docassemble.webapp.create_tables $DA_CONFIG_FILE" www-data
fi

if [ -f /etc/syslog-ng/syslog-ng.conf ] && [ ! -f /usr/share/docassemble/webapp/syslog-ng-orig.conf ]; then
    cp /etc/syslog-ng/syslog-ng.conf /usr/share/docassemble/webapp/syslog-ng-orig.conf
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

if [ "$OTHERLOGSERVER" = false ] && [ -f ${LOGDIRECTORY:-/usr/share/docassemble/log}/docassemble.log ]; then
    chown www-data.www-data ${LOGDIRECTORY:-/usr/share/docassemble/log}/docassemble.log
fi

if [[ $CONTAINERROLE =~ .*:(log):.* ]] || [ "$OTHERLOGSERVER" = true ]; then
    if [ -d /etc/syslog-ng ]; then
	if [ "$OTHERLOGSERVER" = true ]; then
	    cp /usr/share/docassemble/webapp/syslog-ng-docker.conf /etc/syslog-ng/syslog-ng.conf
	    cp /usr/share/docassemble/webapp/docassemble-syslog-ng.conf /etc/syslog-ng/conf.d/docassemble.conf
	else
	    rm -f /etc/syslog-ng/conf.d/docassemble.conf
	    cp /usr/share/docassemble/webapp/syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
	fi
	supervisorctl --serverurl http://localhost:9001 start syslogng
    fi
fi

if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]] && [ "$REDISRUNNING" = false ]; then
    supervisorctl --serverurl http://localhost:9001 start redis
fi

if [[ $CONTAINERROLE =~ .*:(all|rabbitmq):.* ]] && [ "$RABBITMQRUNNING" = false ]; then
    supervisorctl --serverurl http://localhost:9001 start rabbitmq
fi

su -c "source $DA_ACTIVATE && python -m docassemble.webapp.update $DA_CONFIG_FILE" www-data || exit 1

if su -c "source $DA_ACTIVATE && celery -A docassemble.webapp.worker status" www-data 2>&1 | grep -q `hostname`; then
    CELERYRUNNING=true;
else
    CELERYRUNNING=false;
fi

if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]] && [ "$CELERYRUNNING" = false ]; then
    supervisorctl --serverurl http://localhost:9001 start celery
fi

if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [ "$APACHERUNNING" = false ]; then
    rm -f /etc/apache2/ports.conf
fi

if [ ! -f /usr/share/docassemble/certs/apache.key ] && [ -f /usr/share/docassemble/certs/apache.key.orig ]; then
    mv /usr/share/docassemble/certs/apache.key.orig /usr/share/docassemble/certs/apache.key
fi
if [ ! -f /usr/share/docassemble/certs/apache.crt ] && [ -f /usr/share/docassemble/certs/apache.crt.orig ]; then
    mv /usr/share/docassemble/certs/apache.crt.orig /usr/share/docassemble/certs/apache.crt
fi
if [ ! -f /usr/share/docassemble/certs/apache.ca.pem ] && [ -f /usr/share/docassemble/certs/apache.ca.pem.orig ]; then
    mv /usr/share/docassemble/certs/apache.ca.pem.orig /usr/share/docassemble/certs/apache.ca.pem
fi
if [ ! -f /usr/share/docassemble/certs/exim.key ] && [ -f /usr/share/docassemble/certs/exim.key.orig ]; then
    mv /usr/share/docassemble/certs/exim.key.orig /usr/share/docassemble/certs/exim.key
fi
if [ ! -f /usr/share/docassemble/certs/exim.crt ] && [ -f /usr/share/docassemble/certs/exim.crt.orig ]; then
    mv /usr/share/docassemble/certs/exim.crt.orig /usr/share/docassemble/certs/exim.crt
fi
python -m docassemble.webapp.install_certs $DA_CONFIG_FILE || exit 1

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [ "$APACHERUNNING" = false ]; then
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
	    cd /usr/share/docassemble/letsencrypt 
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
	if [ "${USELETSENCRYPT:-none}" != "none" ]; then
	    cd /
	    rm -f /tmp/letsencrypt.tar.gz
	    tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
	    s3cmd -q put /tmp/letsencrypt.tar.gz 's3://'${S3BUCKET}/letsencrypt.tar.gz
	fi
	s3cmd -q sync /etc/apache2/sites-available/ 's3://'${S3BUCKET}/apache/
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	if [ "${USELETSENCRYPT:-none}" != "none" ]; then
	    cd /
	    rm -f /tmp/letsencrypt.tar.gz
	    tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
	    blob-cmd -f cp /tmp/letsencrypt.tar.gz "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/letsencrypt.tar.gz"
	fi
	for the_file in $(find /etc/apache2/sites-available/ -type f); do
	    target_file=`basename $the_file`
	    blob-cmd -f cp $the_file "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/apache/$target_file" 
	done
    else
	if [ "${USELETSENCRYPT:-none}" != "none" ]; then
	    cd /
	    rm -f /usr/share/docassemble/backup/letsencrypt.tar.gz
	    tar -zcf /usr/share/docassemble/backup/letsencrypt.tar.gz etc/letsencrypt
	fi
	rm -rf /usr/share/docassemble/backup/apache
	cp -r /etc/apache2/sites-available /usr/share/docassemble/backup/apache
    fi
fi

if [[ $CONTAINERROLE =~ .*:(log):.* ]] && [ "$APACHERUNNING" = false ]; then
    echo "Listen 8080" >> /etc/apache2/ports.conf
    a2enmod cgid
    a2ensite docassemble-log
fi

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
    supervisorctl --serverurl http://localhost:9001 start websockets
fi

if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [ "$APACHERUNNING" = false ]; then
    supervisorctl --serverurl http://localhost:9001 start apache2
fi

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

su -c "source $DA_ACTIVATE && python -m docassemble.webapp.register $DA_CONFIG_FILE" www-data

if [ "$CRONRUNNING" = false ]; then
   supervisorctl --serverurl http://localhost:9001 start cron
fi

if [[ $CONTAINERROLE =~ .*:(all|mail):.* ]]; then
    echo 'hide pgsql_servers = '${DBHOST}'::'${DBPORT}'/'${DBNAME}'/'${DBUSER}'/'${DBPASSWORD} > /etc/exim4/pginfo
    echo 'DAQUERY = select short from '${DBTABLEPREFIX}"shortener where short='\${quote_pgsql:\$local_part}'" >> /etc/exim4/pginfo
    if [ -f /etc/ssl/docassemble/exim.crt ] && [ -f /etc/ssl/docassemble/exim.key ]; then
	cp /etc/ssl/docassemble/exim.crt /etc/exim4/exim.crt
	cp /etc/ssl/docassemble/exim.key /etc/exim4/exim.key
	chown root.Debian-exim /etc/exim4/exim.crt
	chown root.Debian-exim /etc/exim4/exim.key
	chmod 640 /etc/exim4/exim.crt
	chmod 640 /etc/exim4/exim.key
	echo 'MAIN_TLS_ENABLE = yes' >> /etc/exim4/pginfo
    elif [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [ "${USELETSENCRYPT:-false}" == "true" ] && [ -f /etc/letsencrypt/live/${DAHOSTNAME}/cert.pem ] && [ -f /etc/letsencrypt/live/${DAHOSTNAME}/privkey.pem ]; then
	cp /etc/letsencrypt/live/${DAHOSTNAME}/fullchain.pem /etc/exim4/exim.crt
	cp /etc/letsencrypt/live/${DAHOSTNAME}/privkey.pem /etc/exim4/exim.key
	chown root.Debian-exim /etc/exim4/exim.crt
	chown root.Debian-exim /etc/exim4/exim.key
	chmod 640 /etc/exim4/exim.crt
	chmod 640 /etc/exim4/exim.key
	echo 'MAIN_TLS_ENABLE = yes' >> /etc/exim4/pginfo
    else
	echo 'MAIN_TLS_ENABLE = no' >> /etc/exim4/pginfo
    fi
    chmod og-rwx /etc/exim4/pginfo
    supervisorctl --serverurl http://localhost:9001 start exim4
fi

function deregister {
    su -c "source $DA_ACTIVATE && python -m docassemble.webapp.deregister $DA_CONFIG_FILE" www-data
    if [ "${S3ENABLE:-false}" == "true" ]; then
	su -c "source $DA_ACTIVATE && python -m docassemble.webapp.cloud_deregister" www-data 
	if [[ $CONTAINERROLE =~ .*:(all|log):.* ]]; then
	    s3cmd -q sync /usr/share/docassemble/log/ s3://${S3BUCKET}/log/
	fi
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	su -c "source $DA_ACTIVATE && python -m docassemble.webapp.cloud_deregister" www-data 
	if [[ $CONTAINERROLE =~ .*:(all|log):.* ]]; then
	    for the_file in $(find /usr/share/docassemble/log -type f); do
		target_file=`basename $the_file`
		blob-cmd -f cp $the_file "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/log/$target_file" 
	    done
	fi
    else
	if [[ $CONTAINERROLE =~ .*:(all|log):.* ]]; then
	    rm -rf /usr/share/docassemble/backup/log
	    cp -r /usr/share/docassemble/log /usr/share/docassemble/backup/log
	    rm -rf /usr/share/docassemble/backup/apachelogs
	    cp -r /var/log/apache2 /usr/share/docassemble/backup/apachelogs
	fi
	rm -f /usr/share/docassemble/backup/config.yml
	cp /usr/share/docassemble/config/config.yml /usr/share/docassemble/backup/config.yml
	rm -rf /usr/share/docassemble/backup/files
	cp -r /usr/share/docassemble/files /usr/share/docassemble/backup/
    fi
    echo "finished shutting down initialize" >&2
    kill %1
    exit 0
}

trap deregister SIGINT SIGTERM

echo "initialize finished" >&2
sleep infinity &
wait %1
