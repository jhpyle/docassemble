#!/bin/bash

export DA_ACTIVATE="${DA_PYTHON:-/usr/share/docassemble/local}/bin/activate"

source /dev/stdin < <(su -c "source $DA_ACTIVATE && python -m docassemble.base.read_config" www-data)

if [ "${S3ENABLE:-null}" == "null" ] && [ "${S3BUCKET:-null}" != "null" ]; then
    export S3ENABLE=true
fi

if [ "${S3ENABLE:-null}" == "true" ] && [ "${S3BUCKET:-null}" != "null" ] && [ "${S3ACCESSKEY:-null}" != "null" ] && [ "${S3SECRETACCESSKEY:-null}" != "null" ]; then
    export AWS_ACCESS_KEY_ID=$S3ACCESSKEY
    export AWS_SECRET_ACCESS_KEY=$S3SECRETACCESSKEY
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
	s3cmd -q put "/var/lib/redis/dump.rdb" s3://${S3BUCKET}/redis.rdb
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	blob-cmd -f cp "/var/lib/redis/dump.rdb" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/redis.rdb"
    else
	cp /var/lib/redis/dump.rdb /usr/share/docassemble/backup/redis.rdb
    fi
    exit 0
}

trap stopfunc SIGINT SIGTERM

redis-server /etc/redis/redis.conf &
wait %1
