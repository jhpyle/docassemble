#! /bin/bash

export CONTAINERROLE=":${CONTAINERROLE:-all}:"

if [[ $CONTAINERROLE =~ .*:(log):.* ]] && [ -d /etc/syslog-ng ]; then
    supervisorctl --serverurl http://localhost:9001 restart syslogng
fi
