#! /bin/bash

export DA_CONFIG_FILE_DIST=/usr/share/docassemble/config/config.yml.dist
export DA_CONFIG_FILE=/usr/share/docassemble/config/config.yml
export CONTAINERROLE=":${CONTAINERROLE-all}:"
source /usr/share/docassemble/local/bin/activate

function deregister {
    python -m docassemble.webapp.deregister
    python -m docassemble.webapp.s3deregister
}

if [ "${S3ENABLE-null}" == "null" ] && [ "${S3BUCKET-null}" != "null" ]; then
    export S3ENABLE=true
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

python -m docassemble.webapp.update_config $DA_CONFIG_FILE || exit 1

source /dev/stdin < <(python -m docassemble.base.read_config $DA_CONFIG_FILE)

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

python -m docassemble.webapp.s3register $DA_CONFIG_FILE

if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]]; then
    supervisorctl --serverurl http://localhost:9001 start postgres || exit 1
    sleep 4
    dbexists=`su -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='${DBNAME-docassemble}'\"" postgres`
    roleexists=`su -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='${DBUSER-docassemble}'\"" postgres`
    if [ -z "$roleexists" ]; then
	echo "create role "${DBUSER-docassemble}" with login password '"${DBPASSWORD-abc123}"';" | su -c psql postgres || exit 1
    fi
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

trap deregister SIGINT SIGTERM

sleep infinity &
wait %1
