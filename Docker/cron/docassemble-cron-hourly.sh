#! /bin/bash

export DA_CONFIG_FILE=/usr/share/docassemble/config/config.yml
export CONTAINERROLE=":${CONTAINERROLE:-all}:"
source /usr/share/docassemble/local/bin/activate

if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]]; then
    /usr/share/docassemble/webapp/run-cron.sh cron_hourly
fi

if [[ $CONTAINERROLE =~ .*:(all|redis):.* ]]; then
    su -c "/usr/share/docassemble/local/bin/python -m docassemble.webapp.cleanup_sessions $DA_CONFIG_FILE" www-data
fi

