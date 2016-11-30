#! /bin/bash

export CRONTYPE=${1:-cron_daily}
export DA_CONFIG_FILE=/usr/share/docassemble/config/config.yml
source /usr/share/docassemble/local/bin/activate

exec su -c "/usr/share/docassemble/local/bin/python -m docassemble.webapp.cron $DA_CONFIG_FILE -type $CRONTYPE" www-data
