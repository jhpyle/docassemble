#! /bin/bash

if [[ $CONTAINERROLE =~ .*:(all|sql):.* ]]; then
    /usr/share/docassemble/webapp/run-cron.sh cron_monthly
fi
