#!/bin/bash

trap "{ echo stopping postgres ; pg_ctlcluster --force 9.4 main stop ; sleep 4 ; exit 0 ; }" SIGINT SIGTERM

source /usr/share/postgresql-common/init.d-functions

if [ -d /var/run/postgresql ]; then
    chmod 2775 /var/run/postgresql
else
    install -d -m 2775 -o postgres -g postgres /var/run/postgresql
fi

su postgres -c "/usr/lib/postgresql/9.4/bin/postgres -D /var/lib/postgresql/9.4/main -c config_file=/etc/postgresql/9.4/main/postgresql.conf" &
wait %1

