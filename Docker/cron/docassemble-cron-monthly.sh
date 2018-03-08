#! /bin/bash

export DA_CONFIG_FILE=/usr/share/docassemble/config/config.yml
export CONTAINERROLE=":${CONTAINERROLE:-all}:"
source /usr/share/docassemble/local/bin/activate
source /dev/stdin < <(su -c "source /usr/share/docassemble/local/bin/activate && python -m docassemble.base.read_config $DA_CONFIG_FILE" www-data)

if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    /usr/share/docassemble/webapp/run-cron.sh cron_monthly
fi
