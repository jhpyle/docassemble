#!/bin/bash

function stopfunc {
    sleep 3
    exit 0
}

trap stopfunc SIGINT SIGTERM

su -c "source /usr/share/docassemble/local/bin/activate && python -m docassemble.webapp.socketserver " www-data &

/usr/sbin/apache2ctl -DFOREGROUND
