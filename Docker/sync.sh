#! /bin/bash

export CONTAINERROLE=":${CONTAINERROLE:-all}:"

if [[ $CONTAINERROLE =~ .*:(log):.* ]]; then
    rsync -auq --delete /usr/share/docassemble/log/ /var/www/html/log/ && chown -R www-data.www-data /var/www/html/log
fi
if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
    rsync -auq /var/log/apache2/ /usr/share/docassemble/log/ && chown -R www-data.www-data /usr/share/docassemble/log
fi
