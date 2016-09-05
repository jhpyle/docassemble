#! /bin/bash

export DA_CONFIG_FILE_DIST=/usr/share/docassemble/config/config.yml.dist
export DA_CONFIG_FILE=/usr/share/docassemble/config/config.yml
export CONTAINERROLE=":${CONTAINERROLE-all}:"
source /usr/share/docassemble/local/bin/activate

if [ "${S3ENABLE-null}" == "null" ] && [ "${S3BUCKET-null}" != "null" ]; then
    export S3ENABLE=true
fi

if [ "${S3ENABLE-null}" == "true" ] && [ "${S3BUCKET-null}" != "null" ] && [ "${S3ACCESSKEY-null}" != "null" ] && [ "${S3SECRETACCESSKEY-null}" != "null" ]; then
    export AWS_ACCESS_KEY_ID=$S3ACCESSKEY
    export AWS_SECRET_ACCESS_KEY=$S3SECRETACCESSKEY
fi

if [ "${S3ENABLE-false}" == "true" ]; then
    if [[ $CONTAINERROLE =~ .*:(all|web):.* ]] && [[ $(s3cmd ls s3://${S3BUCKET}/letsencrypt) ]]; then
	s3cmd -q sync s3://${S3BUCKET}/letsencrypt/ /etc/letsencrypt/
    fi
    if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]] && [[ $(s3cmd ls s3://${S3BUCKET}/apache) ]]; then
	s3cmd -q sync s3://${S3BUCKET}/apache/ /etc/apache2/sites-available/
    fi
    if [[ $CONTAINERROLE =~ .*:(all|log):.* ]] && [[ $(s3cmd ls s3://${S3BUCKET}/log) ]]; then
	s3cmd -q sync s3://${S3BUCKET}/log/ /usr/share/docassemble/log/
    fi
    if [[ $(s3cmd ls s3://${S3BUCKET}/config.yml) ]]; then
	rm -f $DA_CONFIG_FILE
	s3cmd -q get s3://${S3BUCKET}/config.yml $DA_CONFIG_FILE
    fi
fi

if [ ! -f $DA_CONFIG_FILE ]; then
    sed -e 's@{{DBPREFIX}}@'"${DBPREFIX-postgresql+psycopg2://}"'@' \
	-e 's/{{DBNAME}}/'"${DBNAME-docassemble}"'/' \
	-e 's/{{DBUSER}}/'"${DBUSER-docassemble}"'/' \
	-e 's/{{DBPASSWORD}}/'"${DBPASSWORD-abc123}"'/' \
	-e 's/{{DBHOST}}/'"${DBHOST-null}"'/' \
	-e 's/{{DBPORT}}/'"${DBPORT-null}"'/' \
	-e 's/{{DBTABLEPREFIX}}/'"${DBTABLEPREFIX-null}"'/' \
	-e 's/{{S3ENABLE}}/'"${S3ENABLE-false}"'/' \
	-e 's/{{S3ACCESSKEY}}/'"${S3ACCESSKEY-null}"'/' \
	-e 's/{{S3SECRETACCESSKEY}}/'"${S3SECRETACCESSKEY-null}"'/' \
	-e 's/{{S3BUCKET}}/'"${S3BUCKET-null}"'/' \
	-e 's/{{REDIS}}/'"${REDIS-null}"'/' \
	-e 's/{{RABBITMQ}}/'"${RABBITMQ-null}"'/' \
	-e 's/{{EC2}}/'"${EC2-false}"'/' \
	-e 's/{{LOGSERVER}}/'"${LOGSERVER-null}"'/' \
	$DA_CONFIG_FILE_DIST > $DA_CONFIG_FILE || exit 1
    chown www-data.www-data $DA_CONFIG_FILE
fi

source /dev/stdin < <(python -m docassemble.base.read_config $DA_CONFIG_FILE)

if [ "${EC2-false}" == "true" ]; then
    export LOCAL_HOSTNAME=`curl http://169.254.169.254/latest/meta-data/local-hostname`
else
    export LOCAL_HOSTNAME=`hostname --fqdn`
fi

if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]]; then
    rm -f /etc/apache2/sites-available/000-default.conf
    rm -f /etc/apache2/sites-available/default-ssl.conf
    a2dissite -q 000-default &> /dev/null
    a2dissite -q default-ssl &> /dev/null
    if [ "${DAHOSTNAME-none}" != "none" ]; then
	if [ ! -f /etc/apache2/sites-available/docassemble-ssl.conf ] || [ "${USELETSENCRYPT-none}" == "none" ] || [ "${USEHTTPS-false}" == "false" ]; then
	    sed -e 's/#ServerName {{DAHOSTNAME}}/ServerName '"${DAHOSTNAME}"'/' \
		/usr/share/docassemble/config/docassemble-ssl.conf.dist > /etc/apache2/sites-available/docassemble-ssl.conf || exit 1
	    rm -f /etc/letsencrypt/da_using_lets_encrypt
	fi
	if [ ! -f /etc/apache2/sites-available/docassemble-http.conf ] || [ "${USELETSENCRYPT-none}" == "none" ] || [ "${USEHTTPS-false}" == "false" ]; then
	    sed -e 's/#ServerName {{DAHOSTNAME}}/ServerName '"${DAHOSTNAME}"'/' \
		/usr/share/docassemble/config/docassemble-http.conf.dist > /etc/apache2/sites-available/docassemble-http.conf || exit 1
	    rm -f /etc/letsencrypt/da_using_lets_encrypt
	fi
	if [ ! -f /etc/apache2/sites-available/docassemble-log.conf ]; then
	    sed -e 's/#ServerName {{DAHOSTNAME}}/ServerName '"${DAHOSTNAME}"'/' \
		/usr/share/docassemble/config/docassemble-log.conf.dist > /etc/apache2/sites-available/docassemble-log.conf || exit 1
	fi
    fi
    a2ensite docassemble-http
fi

if [ "${LOCALE-undefined}" != "undefined" ]; then
    set -- $LOCALE
    DA_LANGUAGE=$1
    grep -q "^$LOCALE" /etc/locale.gen || { echo $LOCALE >> /etc/locale.gen && locale-gen ; }
    update-locale LANG=$DA_LANGUAGE
fi

if [ "${TIMEZONE-undefined}" != "undefined" ]; then
    echo $TIMEZONE > /etc/timezone
    dpkg-reconfigure -f noninteractive tzdata
fi

if [ "${S3ENABLE-false}" == "true" ]; then
    python -m docassemble.webapp.s3register $DA_CONFIG_FILE
fi

if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]]; then
    supervisorctl --serverurl http://localhost:9001 start postgres || exit 1
    while ! pg_isready; do sleep 1; done
    roleexists=`su -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='${DBUSER-docassemble}'\"" postgres`
    if [ -z "$roleexists" ]; then
	echo "create role "${DBUSER-docassemble}" with login password '"${DBPASSWORD-abc123}"';" | su -c psql postgres || exit 1
    fi
    if [ "${S3ENABLE-false}" == "true" ] && [[ $(s3cmd ls s3://${S3BUCKET}/postgres) ]]; then
	PGBACKUPDIR=`mktemp -d`
	s3cmd -q sync s3://${S3BUCKET}/postgres/ "$PGBACKUPDIR/"
	cd "$PGBACKUPDIR"
	for db in $( ls ); do
	    pg_restore -F c -C -c $db | su -c psql postgres
	done
    fi
    dbexists=`su -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='${DBNAME-docassemble}'\"" postgres`
    if [ -z "$dbexists" ]; then
	echo "create database "${DBNAME-docassemble}" owner "${DBUSER-docassemble}";" | su -c psql postgres || exit 1
    fi
    python -m docassemble.webapp.create_tables $DA_CONFIG_FILE
fi

if [ -f /etc/syslog-ng/syslog-ng.conf ] && [ ! -f /usr/share/docassemble/webapp/syslog-ng-orig.conf ]; then
    cp /etc/syslog-ng/syslog-ng.conf /usr/share/docassemble/webapp/syslog-ng-orig.conf
fi

OTHERLOGSERVER=false

if [[ $CONTAINERROLE =~ .*:(web|celery):.* ]]; then
    if [ "${LOGSERVER-undefined}" == "undefined" ]; then
	DEFINEDLOGSERVER=`python -m docassemble.webapp.logserver`
	if [ "${DEFINEDLOGSERVER}" != ""]; then
	    export LOGSERVER="${DEFINEDLOGSERVER}"
	fi
    fi
    if [ "${LOGSERVER-undefined}" != "undefined" ]; then
	OTHERLOGSERVER=true
    fi
fi

if [[ $CONTAINERROLE =~ .*:(log):.* ]] || [ "${LOGSERVER-undefined}" == "null" ]; then
    OTHERLOGSERVER=false
fi

if [ "$OTHERLOGSERVER" = false ] && [ -f /usr/share/docassemble/log/docassemble.log ]; then
    chown www-data.www-data /usr/share/docassemble/log/docassemble.log
fi

if [[ $CONTAINERROLE =~ .*:(log):.* ]] || [ "$OTHERLOGSERVER" = true ]; then
    if [ -d /etc/syslog-ng ]; then
	if [ "$OTHERLOGSERVER" = true ]; then
	    cp /usr/share/docassemble/webapp/syslog-ng-orig.conf /etc/syslog-ng/syslog-ng.conf
	    cp /usr/share/docassemble/webapp/docassemble-syslog-ng.conf /etc/syslog-ng/conf.d/docassemble
	else
	    rm -f /etc/syslog-ng/conf.d/docassemble
	    cp /usr/share/docassemble/webapp/syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
	fi
	supervisorctl --serverurl http://localhost:9001 start syslogng
    fi
fi

if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]]; then
    supervisorctl --serverurl http://localhost:9001 start redis
fi

if [[ $CONTAINERROLE =~ .*:(all|rabbitmq):.* ]]; then
    supervisorctl --serverurl http://localhost:9001 start rabbitmq
fi

if [[ $CONTAINERROLE =~ .*:(all|web|celery):.* ]]; then
    python -m docassemble.webapp.update $DA_CONFIG_FILE || exit 1
fi

if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]]; then
    supervisorctl --serverurl http://localhost:9001 start celery
fi

if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]]; then
    rm -f /etc/apache2/ports.conf
fi

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
    echo "Listen 80" >> /etc/apache2/ports.conf
    if [ ! -f /usr/share/docassemble/certs/docassemble.key ] && [ -f /usr/share/docassemble/certs/docassemble.key.orig ]; then
	mv /usr/share/docassemble/certs/docassemble.key.orig /usr/share/docassemble/certs/docassemble.key
    fi
    if [ ! -f /usr/share/docassemble/certs/docassemble.crt ] && [ -f /usr/share/docassemble/certs/docassemble.crt.orig ]; then
	mv /usr/share/docassemble/certs/docassemble.crt.orig /usr/share/docassemble/certs/docassemble.crt
    fi
    if [ ! -f /usr/share/docassemble/certs/docassemble.ca.pem ] && [ -f /usr/share/docassemble/certs/docassemble.ca.pem.orig ]; then
	mv /usr/share/docassemble/certs/docassemble.ca.pem.orig /usr/share/docassemble/certs/docassemble.ca.pem
    fi
    python -m docassemble.webapp.install_certs $DA_CONFIG_FILE || exit 1
    if [ "${USEHTTPS-false}" == "true" ]; then
	echo "Listen 443" >> /etc/apache2/ports.conf
	a2enmod ssl
	a2ensite docassemble-ssl
	if [ "${USELETSENCRYPT-false}" == "true" ]; then
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
	a2dissite docassemble-ssl
    fi
    if [ "${S3ENABLE-false}" == "true" ]; then
	s3cmd -q sync /etc/letsencrypt/ 's3://'${S3BUCKET}/letsencrypt/ 
	s3cmd -q sync /etc/apache2/sites-available/ 's3://'${S3BUCKET}/apache/
    fi
fi

if [[ $CONTAINERROLE =~ .*:(all|log):.* ]]; then
    echo "Listen 8080" >> /etc/apache2/ports.conf
    a2enmod cgid
    a2ensite docassemble-log
fi

if [[ $CONTAINERROLE =~ .*:(all|web|log):.* ]]; then
    supervisorctl --serverurl http://localhost:9001 start apache2
fi

python -m docassemble.webapp.register $DA_CONFIG_FILE

function deregister {
    python -m docassemble.webapp.deregister
    if [ "${S3ENABLE-false}" == "true" ]; then
	python -m docassemble.webapp.s3deregister
	if [[ $CONTAINERROLE =~ .*:(all|log):.* ]]; then
	    s3cmd -q sync /usr/share/docassemble/log/ s3://${S3BUCKET}/log/
	fi
    fi
}

trap deregister SIGINT SIGTERM

sleep infinity &
wait %1
