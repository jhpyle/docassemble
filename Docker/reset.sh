#! /bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
source "${DA_PYTHON:-${DA_ROOT}/local}/bin/activate"
export CONTAINERROLE=":${CONTAINERROLE:-all}:"
export HOME=/var/www

python -m docassemble.webapp.restart

#if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
#    supervisorctl --serverurl http://localhost:9001 stop apache2 || exit 1
#    sleep 1
#    supervisorctl --serverurl http://localhost:9001 start apache2 || exit 1
#fi

if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]]; then
	supervisorctl --serverurl http://localhost:9001 stop celery || exit 1
	sleep 1
	supervisorctl --serverurl http://localhost:9001 start celery || exit 1
fi

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
	supervisorctl --serverurl http://localhost:9001 stop websockets || exit 1
	sleep 1
	supervisorctl --serverurl http://localhost:9001 start websockets || exit 1
fi

exit 0
