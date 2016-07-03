#! /bin/bash

if [ "${USEHTTPS-false}" == "true" ]; then
    if [ "${USELETSENCRYPT-false}" == "true" ]; then
	if [ -f /usr/share/docassemble/config/using_lets_encrypt ]; then
 	    cd /usr/share/docassemble/letsencrypt
	    supervisorctl --serverurl http://localhost:9001 stop apache2
	    ./letsencrypt-auto renew
	    /etc/init.d/apache2 stop
	    supervisorctl --serverurl http://localhost:9001 start apache2
	fi
    fi
fi
