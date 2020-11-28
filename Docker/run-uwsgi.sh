#!/bin/bash

export DEBIAN_FRONTEND=noninteractive
export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
export DAPYTHONVERSION="${DAPYTHONVERSION:-3}"
export DA_DEFAULT_LOCAL="local3.8"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
source "${DA_ACTIVATE}"
source /dev/stdin < <(python -m docassemble.base.read_config "$DA_CONFIG_FILE")

set -- $LOCALE
export LANG=$1
export HOME=/var/www

function stopfunc {
    UWSGI_PID=$(</var/run/uwsgi/uwsgi.pid) || exit 0
    echo "Sending stop command" >&2
    kill -INT $UWSGI_PID
    echo "Waiting for uwsgi to stop" >&2
    wait $UWSGI_PID
    echo "uwsgi stopped" >&2
    exit 0
}

trap stopfunc SIGINT SIGTERM

uwsgi --ini "${DA_ROOT}/config/docassemble.ini" &
wait %1
