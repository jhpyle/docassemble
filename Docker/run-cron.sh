#! /bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DAPYTHONVERSION="${DAPYTHONVERSION:-3}"
export DA_DEFAULT_LOCAL="local3.8"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"

source "${DA_ACTIVATE}"

export HOME=/var/www
export CRONTYPE=${1:-cron_daily}

export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
source /dev/stdin < <(su -c "source \"$DA_ACTIVATE\" && python -m docassemble.base.read_config \"$DA_CONFIG_FILE\"" www-data)

set -- $LOCALE
export LANG=$1

exec nice -n 19 su -c "source \"$DA_ACTIVATE\" && python -m docassemble.webapp.cron \"$DA_CONFIG_FILE\" -type $CRONTYPE" www-data
