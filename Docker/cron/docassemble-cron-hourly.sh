#! /bin/bash

export CONTAINERROLE=":${CONTAINERROLE:-all}:"

if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]]; then
    /usr/share/docassemble/webapp/run-cron.sh cron_hourly
fi
