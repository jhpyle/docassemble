#! /bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DAPYTHONVERSION="${DAPYTHONVERSION:-3}"
export DA_DEFAULT_LOCAL="local3.8"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
source "${DA_ACTIVATE}"

export CONTAINERROLE=":${CONTAINERROLE:-all}:"
export HOME=/var/www

source /dev/stdin < <(python -m docassemble.base.read_config "$DA_CONFIG_FILE")

# if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
#     supervisorctl --serverurl http://localhost:9001 stop nginx || exit 1
# fi

python -m docassemble.webapp.restart

#if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
#    supervisorctl --serverurl http://localhost:9001 stop apache2 || exit 1
#    sleep 1
#    supervisorctl --serverurl http://localhost:9001 start apache2 || exit 1
#fi

if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]]; then
    supervisorctl --serverurl http://localhost:9001 stop celery || exit 1
    if [[ $CONTAINERROLE =~ .*:(all|rabbitmq):.* ]]; then
	supervisorctl --serverurl http://localhost:9001 stop rabbitmq || exit 1
    fi
    sleep 1
    if [[ $CONTAINERROLE =~ .*:(all|rabbitmq):.* ]]; then
	supervisorctl --serverurl http://localhost:9001 start rabbitmq || exit 1
    fi
    sleep 1
    supervisorctl --serverurl http://localhost:9001 start celery || exit 1
fi

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
    supervisorctl --serverurl http://localhost:9001 stop websockets || exit 1
    sleep 1
    supervisorctl --serverurl http://localhost:9001 start websockets || exit 1
fi

# if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
#     supervisorctl --serverurl http://localhost:9001 start nginx || exit 1
# fi

exit 0
