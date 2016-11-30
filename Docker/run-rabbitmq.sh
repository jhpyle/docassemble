#!/bin/bash

trap "{ echo stopping rabbitmq ; rabbitmqctl stop ; exit 0 ; }" SIGINT SIGTERM

rabbitmq-server &
wait %1
