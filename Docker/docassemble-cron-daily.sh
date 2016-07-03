#! /bin/bash

if [ "${CONTAINERROLE-all}" == "all" ]; then
    MONTHDAY=$(date +%m-%d)
    BACKUPDIR=/usr/share/docassemble/backup/$MONTHDAY
    rm -rf $BACKUPDIR
    mkdir -p $BACKUPDIR
    rsync -au /usr/share/docassemble/files $BACKUPDIR/
    rsync -au /usr/share/docassemble/config $BACKUPDIR/
    rsync -au /usr/share/docassemble/log $BACKUPDIR/
    PGBACKUPDIR=$BACKUPDIR/postgres
    mkdir -p $PGBACKUPDIR
    chown postgres.postgres $PGBACKUPDIR
    su postgres -c 'psql -Atc "SELECT datname FROM pg_database" postgres' | grep -v template | awk -v backupdir=$PGBACKUPDIR '{print "su postgres -c \"pg_dump -F c -f " backupdir "/" $1 " " $1 "\""}' | bash
fi
