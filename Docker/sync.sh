#! /bin/bash

export CONTAINERROLE=":${CONTAINERROLE:-all}:"
export LOGDIRECTORY="${LOGDIRECTORY:-/usr/share/docassemble/log}"

if [[ $CONTAINERROLE =~ .*:(log):.* ]]; then
    rsync -auq --delete ${LOGDIRECTORY}/ /var/www/html/log/ && chown -R www-data.www-data /var/www/html/log
fi
if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
    rsync -auq /var/log/apache2/ ${LOGDIRECTORY}/ && chown -R www-data.www-data ${LOGDIRECTORY}
fi
