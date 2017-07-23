#! /bin/bash

export DA_CONFIG_FILE=/usr/share/docassemble/config/config.yml
export CONTAINERROLE=":${CONTAINERROLE:-all}:"
source /usr/share/docassemble/local/bin/activate

for old_dir in $( find /tmp -maxdepth 1 -type d -mmin +60 -path "/tmp/SavedFile*" ); do
    rm -rf "$old_dir"
done	       

for old_dir in $( find /tmp -maxdepth 1 -type f -mmin +60 -path "/tmp/datemp*" ); do
    rm -rf "$old_dir"
done	       

if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    /usr/share/docassemble/webapp/run-cron.sh cron_hourly
    su -c "/usr/share/docassemble/local/bin/python -m docassemble.webapp.cleanup_sessions $DA_CONFIG_FILE" www-data
fi

