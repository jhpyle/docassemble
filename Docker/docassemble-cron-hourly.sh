#! /bin/bash

if [ "${CONTAINERROLE-all}" == "all" ]; then
    /usr/share/docassemble/webapp/run-cron.sh cron_hourly
fi
