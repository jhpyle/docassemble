#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DA_DEFAULT_LOCAL="local3.10"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
source /dev/stdin < <(source "${DA_ACTIVATE}" && python -m docassemble.base.read_config "${DA_CONFIG_FILE}")

source "${DA_ACTIVATE}"

export CONTAINERROLE=":${CONTAINERROLE:-all}:"
export HOME=/var/www

export LC_ALL=C

set -- $LOCALE
export LANG=$1

if [ "${DAREADONLYFILESYSTEM:-false}" == "false" ] && [ "${DAALLOWUPDATES:-true}" == "true" ]; then
    python -m docassemble.webapp.update "$DA_CONFIG_FILE" check_for_updates
fi

exit 0
