#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"

export DA_DEFAULT_LOCAL="local3.8"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"

source "${DA_ACTIVATE}"

export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"
source /dev/stdin < <(source "$DA_ACTIVATE" && python -m docassemble.base.read_config --limited "$DA_CONFIG_FILE")

set -- $LOCALE
export LANG=$1

export HOME=/var/www

exec celery -A docassemble.webapp.worker worker --loglevel=INFO --concurrency=1 -Q single -n worker1@%h
