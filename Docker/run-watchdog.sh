#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DAPYTHONVERSION="${DAPYTHONVERSION:-3}"
export DA_DEFAULT_LOCAL="local3.8"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
source "${DA_ACTIVATE}"

python -m docassemble.webapp.watchdog &

WATCHDOGPID=%1

function stopfunc {
    kill -SIGTERM $WATCHDOGPID
    exit 0
}

trap stopfunc SIGINT SIGTERM

wait $WATCHDOGPID
