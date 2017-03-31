#! /bin/bash

export CRONTYPE=${1:-cron_daily}
export DA_ACTIVATE="${DA_PYTHON:-/usr/share/docassemble/local}/bin/activate"
export HOME=/var/www

exec su -c "source $DA_ACTIVATE && python -m docassemble.webapp.cron -type $CRONTYPE" www-data
