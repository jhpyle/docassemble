#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DA_DEFAULT_LOCAL="local3.10"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
source /dev/stdin < <(su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.base.read_config \"${DA_CONFIG_FILE}\"" www-data)

source "${DA_ACTIVATE}"

set -- $LOCALE
export LANG=$1

function stopfunc {
    redis-cli shutdown
    echo "backing up redis" >&2
    if [ "${S3ENABLE:-false}" == "true" ]; then
	s4cmd -f put "/var/lib/redis/dump.rdb" "s3://${S3BUCKET}/redis.rdb"
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	az storage blob upload --no-progress --overwrite true --only-show-errors --output none --container-name "${AZURECONTAINER}" -f "/var/lib/redis/dump.rdb" -n "redis.rdb"
    else
	cp /var/lib/redis/dump.rdb "${DA_ROOT}/backup/redis.rdb"
    fi
    echo "finished backing up redis" >&2
    rm -f "/var/run/docassemble/status-redis-running"
    exit 0
}

trap stopfunc SIGINT SIGTERM

touch "/var/run/docassemble/status-redis-running"
redis-server /etc/redis/redis.conf &
wait %1
