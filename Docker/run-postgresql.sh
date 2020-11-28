#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DAPYTHONVERSION="${DAPYTHONVERSION:-3}"
export DA_DEFAULT_LOCAL="local3.8"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
source /dev/stdin < <(su -c "source \"${DA_ACTIVATE}\" && python -m docassemble.base.read_config \"${DA_CONFIG_FILE}\"" www-data)

source "${DA_ACTIVATE}"

set -- $LOCALE
export LANG=$1

function cmd_retry() {
    local -r cmd="$@"
    local -r -i max_attempts=4
    local -i attempt_num=1
    until $cmd
    do
        if ((attempt_num==max_attempts))
        then
            echo "Attempt $attempt_num failed.  Not trying again"
            return 1
        else
            if ((attempt_num==1)); then
                echo $cmd
            fi
            echo "Attempt $attempt_num failed."
            sleep $(((attempt_num++)**2))
        fi
    done
}

PGVERSION=`pg_config --version | sed 's/PostgreSQL \([0-9][0-9]*\.[0-9][0-9]*\).*/\1/'`

if [[ $PGVERSION == 10* ]]; then
    PGVERSION=10
fi

if [[ $PGVERSION == 11* ]]; then
    PGVERSION=11
fi

chown -R postgres.postgres /etc/postgresql
chown -R postgres.postgres /var/lib/postgresql
chown -R postgres.postgres /var/run/postgresql
chown -R postgres.postgres /var/log/postgresql

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

if [ "${AZUREENABLE:-null}" == "null" ] && [ "${AZUREACCOUNTNAME:-null}" != "null" ] && [ "${AZUREACCOUNTKEY:-null}" != "null" ] && [ "${AZURECONTAINER:-null}" != "null" ]; then
    export AZUREENABLE=true
fi

if [ "${AZUREENABLE:-false}" == "true" ]; then
    cmd_retry blob-cmd -f -v add-account "${AZUREACCOUNTNAME}" "${AZUREACCOUNTKEY}"
fi

function stopfunc {
    sleep 1
    echo "backing up postgres" >&2
    if [ "${S3ENABLE:-false}" == "true" ] || [ "${AZUREENABLE:-false}" == "true" ]; then
	PGBACKUPDIR=`mktemp -d`
    else
	PGBACKUPDIR="${DA_ROOT}/backup/postgres"
	mkdir -p "$PGBACKUPDIR"
    fi
    chown postgres.postgres "$PGBACKUPDIR"
    su postgres -c 'psql -Atc "SELECT datname FROM pg_database" postgres' | grep -v -e template -e postgres | awk -v backupdir="$PGBACKUPDIR" '{print "cd /tmp; su postgres -c \"pg_dump -F c -f " backupdir "/" $1 " " $1 "\""}' | bash
    if [ "${S3ENABLE:-false}" == "true" ]; then
	s4cmd dsync "$PGBACKUPDIR" "s3://${S3BUCKET}/postgres"
	rm -rf "$PGBACKUPDIR"
    elif [ "${AZUREENABLE:-false}" == "true" ]; then
	for the_file in $(find "$PGBACKUPDIR" -type f); do
	    target_file=`basename $the_file`
	    cmd_retry blob-cmd -f cp "$the_file" "blob://${AZUREACCOUNTNAME}/${AZURECONTAINER}/postgres/${target_file}"
	done
	rm -rf "$PGBACKUPDIR"
    fi
    echo "stopping postgres" >&2
    pg_ctlcluster --force $PGVERSION main stop
    exit 0
}

trap stopfunc SIGINT SIGTERM

#source /usr/share/postgresql-common/init.d-functions

if [ -d /var/run/postgresql ]; then
    chmod 2775 /var/run/postgresql
else
    install -d -m 2775 -o postgres -g postgres /var/run/postgresql
fi

mkdir -p "/var/run/postgresql/${PGVERSION}-main.pg_stat_tmp"
chown -R postgres.postgres "/var/run/postgresql/${PGVERSION}-main.pg_stat_tmp"

su postgres -c "/usr/lib/postgresql/${PGVERSION}/bin/postgres -D /var/lib/postgresql/${PGVERSION}/main -c config_file=/etc/postgresql/${PGVERSION}/main/postgresql.conf" &
wait %1
