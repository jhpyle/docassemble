#! /bin/bash

export CONTAINERROLE=":${CONTAINERROLE:-all}:"

if [ "${S3ENABLE:-null}" == "null" ] && [ "${S3BUCKET:-null}" != "null" ]; then
    export S3ENABLE=true
fi

if [ "${S3ENABLE:-null}" == "true" ] && [ "${S3BUCKET:-null}" != "null" ] && [ "${S3ACCESSKEY:-null}" != "null" ] && [ "${S3SECRETACCESSKEY:-null}" != "null" ]; then
    export AWS_ACCESS_KEY_ID=$S3ACCESSKEY
    export AWS_SECRET_ACCESS_KEY=$S3SECRETACCESSKEY
fi

if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    /usr/share/docassemble/webapp/run-cron.sh cron_weekly
fi

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
    if [ "${USEHTTPS:-false}" == "true" ]; then
	if [ "${USELETSENCRYPT:-false}" == "true" ]; then
	    if [ -f /etc/letsencrypt/da_using_lets_encrypt ]; then
		supervisorctl --serverurl http://localhost:9001 stop apache2
		cd /usr/share/docassemble/letsencrypt
		./letsencrypt-auto renew
		/etc/init.d/apache2 stop
		supervisorctl --serverurl http://localhost:9001 start apache2
		if [ "${S3ENABLE:-false}" == "true" ]; then
		    cd /
		    if [ "${USELETSENCRYPT:-none}" != "none" ]; then
			rm -f /tmp/letsencrypt.tar.gz
			tar -zcf /tmp/letsencrypt.tar.gz etc/letsencrypt
			s3cmd -q put /tmp/letsencrypt.tar.gz 's3://'${S3BUCKET}/letsencrypt.tar.gz
		    fi
		    s3cmd -q sync /etc/apache2/sites-available/ 's3://'${S3BUCKET}/apache/
		fi
		if [[ $CONTAINERROLE =~ .*:all:.* ]]; then
		    cp /etc/letsencrypt/live/${DAHOSTNAME}/fullchain.pem /etc/exim4/exim.crt
		    cp /etc/letsencrypt/live/${DAHOSTNAME}/privkey.pem /etc/exim4/exim.key
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
