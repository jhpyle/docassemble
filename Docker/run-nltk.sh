#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"

export DA_DEFAULT_LOCAL="local3.12"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"

source "${DA_ACTIVATE}"

export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
source /dev/stdin < <(source "$DA_ACTIVATE" && python -m docassemble.base.read_config --limited "$DA_CONFIG_FILE")

python -m docassemble.base.pattern_server &

NLTKPID=%1

function stopfunc {
    kill -SIGTERM $NLTKPID
    rm -f "${NLTKSOCKET:-/var/run/nltk/da_nltk.sock}"
    exit 0
}

trap stopfunc SIGINT SIGTERM

wait $NLTKPID
