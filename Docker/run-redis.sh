#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DAPYTHONVERSION="${DAPYTHONVERSION:-2}"
if [ "${DAPYTHONVERSION}" == "2" ]; then
    export DA_DEFAULT_LOCAL="local"
else
    export DA_DEFAULT_LOCAL="local3.6"
fi
export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
source /dev/stdin < <(su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.base.read_config \"${DA_CONFIG_FILE}\"" www-data)

source "${DA_ACTIVATE}"

set -- $LOCALE
export LANG=$1

if [ "${S3ENABLE:-null}" == "null" ] && [ "${S3BUCKET:-null}" != "null" ]; then
    export S3ENABLE=true
fi

if [ "${S3ENABLE:-null}" == "true" ] && [ "${S3BUCKET:-null}" != "null" ] && [ "${S3ACCESSKEY:-null}" != "null" ] && [ "${S3SECRETACCESSKEY:-null}" != "null" ]; then
    export S3_ACCESS_KEY="${S3ACCESSKEY}"
    export S3_SECRET_KEY="${S3SECRETACCESSKEY}"
fi

if [ "${S3ENDPOINTURL:-null}" != "null" ]; then
    export S4CMD_OPTS="--endpoint-url=\"${S3ENDPOINTURL}\""
fi

if [ "${AZUREENABLE:-null}" == "null" ] && [ "${AZUREACCOUNTNAME:-null}" != "null" ] && [ "${AZUREACCOUNTKEY:-null}" != "null" ] && [ "${AZURECONTAINER:-null}" != "null" ]; then
    export AZUREENABLE=true
fi

if [ "${AZUREENABLE:-false}" == "true" ]; then
    blob-cmd -f -v add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
fi

function stopfunc {
    redis-cli shutdown
    echo backing up redis
    if [ "${S3ENABLE:-false}" == "true" ]; then
	s4cmd -f put "/var/lib/redis/dump.rdb" "s3://${S3BUCKET}/redis.rdb"
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	blob-cmd -f cp "/var/lib/redis/dump.rdb" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/redis.rdb"
    else
	cp /var/lib/redis/dump.rdb "${DA_ROOT}/backup/redis.rdb"
    fi
    exit 0
}

trap stopfunc SIGINT SIGTERM

redis-server /etc/redis/redis.conf &
wait %1
