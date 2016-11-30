#! /bin/bash

export CONTAINERROLE=":${CONTAINERROLE:-all}:"

if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    /usr/share/docassemble/webapp/run-cron.sh cron_monthly
fi
