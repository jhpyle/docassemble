#! /bin/bash

export DA_ACTIVATE="${DA_PYTHON:-/usr/share/docassemble/local}/bin/activate"
export DA_CONFIG_FILE="${DA_CONFIG:-/usr/share/docassemble/config/config.yml}"
source /dev/stdin < <(su -c "source $DA_ACTIVATE && python -m docassemble.base.read_config $DA_CONFIG_FILE" www-data)

export CONTAINERROLE=":${CONTAINERROLE:-all}:"
export LOGDIRECTORY="${LOGDIRECTORY:-/usr/share/docassemble/log}"

if [[ $CONTAINERROLE =~ .*:(log):.* ]]; then
    rsync -auq --delete ${LOGDIRECTORY}/ /var/www/html/log/ && chown -R www-data.www-data /var/www/html/log
fi
if [[ $CONTAINERROLE =~ .*:(all):.* ]]; then
    rsync -auq /var/log/apache2/ ${LOGDIRECTORY}/ && chown -R www-data.www-data ${LOGDIRECTORY}
fi
