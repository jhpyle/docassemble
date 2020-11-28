#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DAPYTHONVERSION="${DAPYTHONVERSION:-3}"
export DA_DEFAULT_LOCAL="local3.8"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
source "${DA_ACTIVATE}"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
source /dev/stdin < <(source "$DA_ACTIVATE" && python -m docassemble.base.read_config "$DA_CONFIG_FILE")

set -- $LOCALE
export LANG=$1

export HOME=/var/www

python -u -m docassemble.webapp.socketserver &

WEBSOCKETSPID=%1

function stopfunc {
    kill -SIGTERM $WEBSOCKETSPID
    exit 0
}

trap stopfunc SIGINT SIGTERM

wait $WEBSOCKETSPID
