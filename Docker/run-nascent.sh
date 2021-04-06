#!/bin/bash

export CONTAINERROLE=":${CONTAINERROLE:-all}:"
export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"

set -- $LOCALE
export LANG=$1

if [ -f /var/run/apache2/apache2.pid ]; then
    APACHE_PID=$(</var/run/apache2/apache2.pid)
    if kill -0 $APACHE_PID &> /dev/null; then
        exit 0
    fi
fi

if [ -f /var/run/nginx.pid ]; then
    NGINX_PID=$(</var/run/nginx.pid)
    if kill -0 $NGINX_PID &> /dev/null; then
        exit 0
    fi
fi

if ! [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
    exit 0
fi

busybox httpd -f -p ${PORT:-80} -h /var/www/nascent
