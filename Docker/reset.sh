#! /bin/bash

source "${DA_PYTHON:-/usr/share/docassemble/local}/bin/activate"
export CONTAINERROLE=":${CONTAINERROLE:-all}:"

python -m docassemble.webapp.restart

if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]]; then
    supervisorctl --serverurl http://localhost:9001 restart celery || exit 1
fi

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
    supervisorctl --serverurl http://localhost:9001 restart websockets || exit 1
fi

exit 0
