#! /bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
export DA_DEFAULT_LOCAL="local3.10"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
source "${DA_ACTIVATE}"
source /dev/stdin < <(python -m docassemble.base.read_config "$DA_CONFIG_FILE" )

if [ "${DAREADONLYFILESYSTEM:-false}" == "true" ]; then
    exit 0
fi

if [ "${DASUPERVISORUSERNAME:-null}" != "null" ]; then
    SUPERVISORCMD="supervisorctl --serverurl http://localhost:9001 --username ${DASUPERVISORUSERNAME} --password ${DASUPERVISORPASSWORD}"
else
    SUPERVISORCMD="supervisorctl --serverurl http://localhost:9001"
fi

if [ -e /var/run/uwsgi/docassemble.sock ]; then
    if [ "${DAROOTOWNED:-false}" == "true" ]; then
	if [ "${DAALLOWUPDATES:-true}" == "true" ] \
	   || [ "${DAENABLEPLAYGROUND:-true}" == "true" ] \
	   || [ "${DAALLOWCONFIGURATIONEDITING:-true}" == "true" ]; then
	    ${SUPERVISORCMD} stop uwsgi > /dev/null || exit 1
	    ${SUPERVISORCMD} start uwsgi > /dev/null || exit 1
	fi
    else
	${SUPERVISORCMD} stop uwsgi > /dev/null || exit 1
	${SUPERVISORCMD} start uwsgi > /dev/null || exit 1
    fi
fi

if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]]; then
    ${SUPERVISORCMD} stop celery > /dev/null || exit 1
    ${SUPERVISORCMD} stop celerysingle > /dev/null || exit 1
    ${SUPERVISORCMD} start celery > /dev/null || exit 1
    ${SUPERVISORCMD} start celerysingle > /dev/null || exit 1
fi

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
    ${SUPERVISORCMD} stop websockets > /dev/null || exit 1
    sleep 1
    ${SUPERVISORCMD} start websockets > /dev/null || exit 1
fi

if ${SUPERVISORCMD} status syslogng | grep -q RUNNING ; then
    ${SUPERVISORCMD} restart syslogng > /dev/null || exit 1
fi
