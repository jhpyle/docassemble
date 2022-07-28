#! /bin/bash

if [ "${DASUPERVISORUSERNAME:-null}" != "null" ]; then
    SUPERVISORCMD="supervisorctl --serverurl http://localhost:9001 --username ${DASUPERVISORUSERNAME} --password ${DASUPERVISORPASSWORD}"
else
    SUPERVISORCMD="supervisorctl --serverurl http://localhost:9001"
fi

${SUPERVISORCMD} start sync > /dev/null
while ${SUPERVISORCMD} status sync | grep -q RUNNING; do
    sleep 1
done
echo "Content-Type: text/plain" && echo && ls /var/www/html/log
