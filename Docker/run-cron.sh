#! /bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/local}/bin/activate"
export HOME=/var/www
export CRONTYPE=${1:-cron_daily}

exec su -c "source $DA_ACTIVATE && python -m docassemble.webapp.cron -type $CRONTYPE" www-data
