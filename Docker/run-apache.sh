#!/bin/bash

function stopfunc {
    sleep 3
    exit 0
}

trap stopfunc SIGINT SIGTERM

/usr/sbin/apache2ctl -DFOREGROUND
