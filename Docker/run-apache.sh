#!/bin/bash

export DA_ACTIVATE="${DA_PYTHON:-/usr/share/docassemble/local}/bin/activate"
export DA_CONFIG_FILE="${DA_CONFIG:-/usr/share/docassemble/config/config.yml}"
source /dev/stdin < <(su -c "source $DA_ACTIVATE && python -m docassemble.base.read_config $DA_CONFIG_FILE" www-data)

function stopfunc {
    /usr/sbin/apache2ctl stop
    exit 0
}

trap stopfunc SIGINT SIGTERM

/usr/sbin/apache2ctl -DFOREGROUND &
wait %1
