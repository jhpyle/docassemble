#! /bin/bash

CRONTYPE=${1-cron_daily}
CONFIG_FILE=/usr/share/docassemble/config/config.yml
source /usr/share/docassemble/local/bin/activate
#echo "Type is $CRONTYPE and config is $CONFIG_FILE"

su -c "/usr/share/docassemble/local/bin/python -m docassemble.webapp.cron $CONFIG_FILE -type $CRONTYPE" www-data
