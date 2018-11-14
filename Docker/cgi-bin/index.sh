#! /bin/bash

supervisorctl --serverurl http://localhost:9001 start sync >/dev/null
while supervisorctl --serverurl http://localhost:9001 status sync | grep -q RUNNING; do
    sleep 1
done
echo "Content-Type: text/plain" && echo && ls /var/www/html/log
