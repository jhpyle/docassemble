#!/bin/bash

PGVERSION=`pg_config --version | sed 's/PostgreSQL \([0-9][0-9]*\.[0-9][0-9]*\).*/\1/'`

export DA_ACTIVATE="${DA_PYTHON:-/usr/share/docassemble/local}/bin/activate"

chown -R postgres.postgres /etc/postgresql
chown -R postgres.postgres /var/lib/postgresql
chown -R postgres.postgres /var/run/postgresql
chown -R postgres.postgres /var/log/postgresql

source /dev/stdin < <(su -c "source $DA_ACTIVATE && python -m docassemble.base.read_config" www-data)

if [ "${S3ENABLE:-null}" == "null" ] && [ "${S3BUCKET:-null}" != "null" ]; then
    export S3ENABLE=true
fi

if [ "${S3ENABLE:-null}" == "true" ] && [ "${S3BUCKET:-null}" != "null" ] && [ "${S3ACCESSKEY:-null}" != "null" ] && [ "${S3SECRETACCESSKEY:-null}" != "null" ]; then
    export AWS_ACCESS_KEY_ID=$S3ACCESSKEY
    export AWS_SECRET_ACCESS_KEY=$S3SECRETACCESSKEY
fi

function stopfunc {
    sleep 1
    echo "backing up postgres" >&2
    if [ "${S3ENABLE:-false}" == "true" ]; then
	PGBACKUPDIR=`mktemp -d`
    else
	PGBACKUPDIR=/usr/share/docassemble/backup/postgres
	mkdir -p $PGBACKUPDIR
    fi
    chown postgres.postgres "$PGBACKUPDIR"
    su postgres -c 'psql -Atc "SELECT datname FROM pg_database" postgres' | grep -v -e template -e postgres | awk -v backupdir="$PGBACKUPDIR" '{print "cd /tmp; su postgres -c \"pg_dump -F c -f " backupdir "/" $1 " " $1 "\""}' | bash
    if [ "${S3ENABLE:-false}" == "true" ]; then
	s3cmd sync "$PGBACKUPDIR/" s3://${S3BUCKET}/postgres/
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

mkdir -p /var/run/postgresql/$PGVERSION-main.pg_stat_tmp
chown -R postgres.postgres /var/run/postgresql/$PGVERSION-main.pg_stat_tmp

su postgres -c "/usr/lib/postgresql/$PGVERSION/bin/postgres -D /var/lib/postgresql/$PGVERSION/main -c config_file=/etc/postgresql/$PGVERSION/main/postgresql.conf" &
wait %1
