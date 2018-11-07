#! /bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/local}/bin/activate"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
export CONTAINERROLE=":${CONTAINERROLE:-all}:"
source /dev/stdin < <(su -c "source $DA_ACTIVATE && python -m docassemble.base.read_config $DA_CONFIG_FILE" www-data)

if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    ${DA_ROOT}/webapp/run-cron.sh cron_monthly
fi
