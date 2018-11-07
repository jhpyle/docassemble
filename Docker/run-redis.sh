#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/local}/bin/activate"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
source /dev/stdin < <(su -c "source $DA_ACTIVATE && python -m docassemble.base.read_config $DA_CONFIG_FILE" www-data)

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

function stopfunc() {
	redis-cli shutdown
	echo backing up redis
	if [ "${S3ENABLE:-false}" == "true" ]; then
		aws s3 cp "/var/lib/redis/dump.rdb" s3://${S3BUCKET}/redis.rdb --quiet
	elif [ "${AZUREENABLE:-false}" == "true" ]; then
		blob-cmd -f cp "/var/lib/redis/dump.rdb" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/redis.rdb"
	else
		cp /var/lib/redis/dump.rdb ${DA_ROOT}/backup/redis.rdb
	fi
	exit 0
}

trap stopfunc SIGINT SIGTERM

redis-server /etc/redis/redis.conf &
wait %1
