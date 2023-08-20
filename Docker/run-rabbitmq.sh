#!/bin/bash

trap "{ echo stopping rabbitmq ; rabbitmqctl stop ; rm -f /var/run/docassemble/status-rabbitmq-running ; exit 0 ; }" SIGINT SIGTERM

rabbitmq-server &
RABBITMQ_PID=%1
while ! rabbitmqstatus &> /dev/null; do
    sleep 1
done
rabbitmqctl stop_app
rabbitmqctl reset
rabbitmqctl start_app
touch "/var/run/docassemble/status-rabbitmq-running"
wait ${RABBITMQ_PID}
