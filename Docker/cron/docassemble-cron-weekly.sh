#! /bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DAPYTHONVERSION="${DAPYTHONVERSION:-3}"
export DA_DEFAULT_LOCAL="local3.8"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
source "${DA_ACTIVATE}"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
export CONTAINERROLE=":${CONTAINERROLE:-all}:"
source /dev/stdin < <(su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.base.read_config \"${DA_CONFIG_FILE}\"" www-data)

set -- $LOCALE
export LANG=$1

if [ "${S3ENABLE:-null}" == "null" ] && [ "${S3BUCKET:-null}" != "null" ]; then
    export S3ENABLE=true
fi

if [ "${S3ENABLE:-null}" == "true" ] && [ "${S3BUCKET:-null}" != "null" ] && [ "${S3ACCESSKEY:-null}" != "null" ] && [ "${S3SECRETACCESSKEY:-null}" != "null" ]; then
    export S3_ACCESS_KEY="$S3ACCESSKEY"
    export S3_SECRET_KEY="$S3SECRETACCESSKEY"
    export AWS_ACCESS_KEY_ID="$S3ACCESSKEY"
    export AWS_SECRET_ACCESS_KEY="$S3SECRETACCESSKEY"
fi

if [ "${S3ENDPOINTURL:-null}" != "null" ]; then
    export S4CMD_OPTS="--endpoint-url=\"${S3ENDPOINTURL}\""
fi

if [ "${AZUREENABLE:-null}" == "null" ] && [ "${AZUREACCOUNTNAME:-null}" != "null" ] && [ "${AZURECONTAINER:-null}" != "null" ]; then
    export AZUREENABLE=true
fi

if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    "${DA_ROOT}/webapp/run-cron.sh" cron_weekly
fi
