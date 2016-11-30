#!/bin/bash

function stopfunc {
    /usr/sbin/apache2ctl stop
    exit 0
}

trap stopfunc SIGINT SIGTERM

/usr/sbin/apache2ctl -DFOREGROUND &
wait %1
